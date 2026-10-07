import os
import json
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, ImageOps

PHOTOS_DIR = Path("/usr/share/nginx/html/photos")
THUMBS_DIR = PHOTOS_DIR / ".thumbs"
OUTPUT_JS = Path("/usr/share/nginx/html/images.js")

# Supported image extensions
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def process_image(rel_path):
    """Processes a single image: generates thumb if missing/stale, returns EXIF metadata."""
    src_path = PHOTOS_DIR / rel_path
    thumb_path = THUMBS_DIR / rel_path.with_suffix(".webp")

    # 1. Skip thumbnail creation if it already exists and source hasn't been updated
    thumb_needed = True
    if thumb_path.exists():
        if thumb_path.stat().st_mtime >= src_path.stat().st_mtime:
            thumb_needed = False

    try:
        with Image.open(src_path) as img:
            # Handle EXIF rotation metadata
            img = ImageOps.exif_transpose(img)
            width, height = img.size

            # Generate thumbnail only if missing or outdated
            if thumb_needed:
                thumb_path.parent.mkdir(parents=True, exist_ok=True)
                thumb_img = img.copy()
                thumb_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                thumb_img.save(thumb_path, "WEBP", quality=80, optimize=True)
                print(f"Generated: {rel_path}")
            else:
                print(f"Cached (Skipped): {rel_path}")

            return {
                "src": f"./photos/{rel_path.as_posix()}",
                "thumb": f"./photos/.thumbs/{rel_path.with_suffix('.webp').as_posix()}",
                "width": width,
                "height": height,
                "alt": rel_path.stem.replace("_", " ").title()
            }
    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        return None

def main():
    start_time = time.time()
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    gallery_sections = {}

    # Gather all images across subdirectories
    all_files = []
    for root, _, files in os.walk(PHOTOS_DIR):
        root_path = Path(root)
        if THUMBS_DIR in root_path.parents or root_path == THUMBS_DIR:
            continue  # Skip hidden .thumbs directory

        for f in files:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTS:
                full_path = root_path / f
                rel_path = full_path.relative_to(PHOTOS_DIR)
                all_files.append(rel_path)

    print(f"Found {len(all_files)} images. Starting incremental scan...")

    # Parallel processing across all available CPU cores
    items_by_section = {}
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_image, rel_path): rel_path for rel_path in all_files}
        
        for future in as_completed(futures):
            rel_path = futures[future]
            result = future.result()
            if result:
                section_name = rel_path.parent.as_posix()
                if section_name == ".":
                    section_name = "General"
                
                if section_name not in items_by_section:
                    items_by_section[section_name] = []
                items_by_section[section_name].append(result)

    # Format output JSON structure for images.js
    formatted_sections = []
    for title, items in sorted(items_by_section.items()):
        formatted_sections.append({
            "title": title,
            "items": sorted(items, key=lambda x: x["src"])
        })

    # Write output JS file
    js_content = f"export const gallerySections = {json.dumps(formatted_sections, indent=2)};\n"
    OUTPUT_JS.write_text(js_content, encoding="utf-8")

    elapsed = time.time() - start_time
    print(f"Finished gallery scan in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
