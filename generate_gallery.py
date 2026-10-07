import os
import json
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, ImageOps

# Base Paths
PHOTOS_DIR = Path("/input")                   # Scans directly from root of mounted folder
THUMBS_DIR = Path("/tmp/thumbs")              # Internal container writeable directory
OUTPUT_JS = Path("/usr/share/nginx/html/images.js")
CACHE_FILE = THUMBS_DIR / ".metadata_cache.json"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def process_image(rel_path_str, cached_meta):
    """Processes an image: uses cached dimensions/mtime if untouched; otherwise opens with Pillow."""
    rel_path = Path(rel_path_str)
    src_path = PHOTOS_DIR / rel_path
    thumb_path = THUMBS_DIR / rel_path

    try:
        src_stat = src_path.stat()
        src_mtime = src_stat.st_mtime
    except Exception as e:
        print(f"Error stat file {src_path}: {e}")
        return None

    meta = cached_meta.get(rel_path_str)
    if meta and meta.get("mtime") == src_mtime and thumb_path.exists():
        return rel_path_str, {
            "src": f"./photos/{rel_path.as_posix()}",
            "thumb": f"./thumbs/{rel_path.as_posix()}",
            "width": meta["width"],
            "height": meta["height"],
            "alt": rel_path.stem.replace("_", " ").title(),
            "mtime": src_mtime
        }

    try:
        with Image.open(src_path) as img:
            img = ImageOps.exif_transpose(img)
            width, height = img.size

            if not thumb_path.exists() or thumb_path.stat().st_mtime < src_mtime:
                thumb_path.parent.mkdir(parents=True, exist_ok=True)
                thumb_img = img.copy()
                thumb_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                
                if thumb_img.mode in ("RGBA", "P"):
                    thumb_img = thumb_img.convert("RGB")
                    
                thumb_img.save(thumb_path, "JPEG", quality=80, optimize=True)
                print(f"Generated thumb: {rel_path}")

            return rel_path_str, {
                "src": f"./photos/{rel_path.as_posix()}",
                "thumb": f"./thumbs/{rel_path.as_posix()}",
                "width": width,
                "height": height,
                "alt": rel_path.stem.replace("_", " ").title(),
                "mtime": src_mtime
            }
    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        return None

def main():
    start_time = time.time()
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    cached_meta = {}
    if CACHE_FILE.exists():
        try:
            cached_meta = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cached_meta = {}

    all_files = []
    for root, _, files in os.walk(PHOTOS_DIR):
        root_path = Path(root)
        for f in files:
            if Path(f).suffix.lower() in IMAGE_EXTS:
                full_path = root_path / f
                rel_path = full_path.relative_to(PHOTOS_DIR)
                all_files.append(rel_path.as_posix())

    print(f"Found {len(all_files)} images under /input. Processing gallery...")

    items_by_section = {}
    new_cache = {}

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_image, rel_path_str, cached_meta): rel_path_str for rel_path_str in all_files}
        
        for future in as_completed(futures):
            res = future.result()
            if res:
                rel_path_str, data = res
                rel_path = Path(rel_path_str)
                
                new_cache[rel_path_str] = {
                    "width": data["width"],
                    "height": data["height"],
                    "mtime": data["mtime"]
                }

                # Set section name to subdirectory name, or "General" if the image is in the root directory
                section_name = rel_path.parent.as_posix()
                if section_name == ".":
                    section_name = "General"
                
                if section_name not in items_by_section:
                    items_by_section[section_name] = []
                
                clean_item = {k: v for k, v in data.items() if k != "mtime"}
                items_by_section[section_name].append(clean_item)

    try:
        CACHE_FILE.write_text(json.dumps(new_cache, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Warning: Failed to write metadata cache: {e}")

    formatted_sections = []
    for title, items in sorted(items_by_section.items()):
        formatted_sections.append({
            "title": title,
            "items": sorted(items, key=lambda x: x["src"])
        })

    js_content = f"export const gallerySections = {json.dumps(formatted_sections, indent=2)};\n"
    OUTPUT_JS.write_text(js_content, encoding="utf-8")

    elapsed = time.time() - start_time
    print(f"Gallery build completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
