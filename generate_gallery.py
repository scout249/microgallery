import os
import json
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, ImageOps

# Base Paths
PHOTOS_DIR = Path("/usr/share/nginx/html/photos")
THUMBS_DIR = Path("/usr/share/nginx/html/thumbs")
OUTPUT_JS = Path("/usr/share/nginx/html/images.js")

# Supported image extensions
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def process_image(rel_path):
    """Processes a single image: generates thumbnail if missing/outdated, returns EXIF metadata."""
    src_path = PHOTOS_DIR / rel_path
    
    # Save thumbs under /thumbs directory matching the relative path, using .jpg extension
    thumb_path = THUMBS_DIR / rel_path

    # Check if thumbnail exists and is up to date
    thumb_needed = True
    if thumb_path.exists():
        if thumb_path.stat().st_mtime >= src_path.stat().st_mtime:
            thumb_needed = False

    try:
        with Image.open(src_path) as img:
            # Respect EXIF orientation tag
            img = ImageOps.exif_transpose(img)
            width, height = img.size

            # Generate thumbnail only if missing or original photo was modified
            if thumb_needed:
                thumb_path.parent.mkdir(parents=True, exist_ok=True)
                thumb_img = img.copy()
                thumb_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                
                # Convert RGBA/P images to RGB before saving as JPEG
                if thumb_img.mode in ("RGBA", "P"):
                    thumb_img = thumb_img.convert("RGB")
                    
                thumb_img.save(thumb_path, "JPEG", quality=80, optimize=True)
                print(f"Generated thumb: {rel_path}")
            else:
                print(f"Cached (Skipped): {rel_path}")

            return {
                "src": f"./photos/{rel_path.as_posix()}",
                "thumb": f"./thumbs/{rel_path.as_posix()}",
                "width": width,
                "height": height,
                "alt": rel_path.stem.replace("_", " ").title()
            }
    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        return None

def main():
    start_time = time.time()
    
    # Ensure thumbnail output directory exists
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    # Gather all images recursively across subdirectories
    all_files = []
    for root, _, files in os.walk(PHOTOS_DIR):
        root_path = Path(root)

        for f in files:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTS:
                full_path = root_path / f
                rel_path = full_path.relative_to(PHOTOS_DIR)
                all_files.append(rel_path)

    print(f"Found {len(all_files)} images. Starting processing...")

    # Parallel processing across CPU cores
    items_by_section = {}
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_image, rel_path): rel_path for rel_path in all_files}
        
        for future in as_completed(futures):
            rel_path = futures[future]
            result = future.result()
            if result:
                # Use parent directory name as section title (or "General" if in root)
                section_name = rel_path.parent.as_posix()
                if section_name == ".":
                    section_name = "General"
                
                if section_name not in items_by_section:
                    items_by_section[section_name] = []
                items_by_section[section_name].append(result)

    # Format sections for images.js
    formatted_sections = []
    for title, items in sorted(items_by_section.items()):
        formatted_sections.append({
            "title": title,
            "items": sorted(items, key=lambda x: x["src"])
        })

    # Output ES Module JS file
    js_content = f"export const gallerySections = {json.dumps(formatted_sections, indent=2)};\n"
    OUTPUT_JS.write_text(js_content, encoding="utf-8")

    elapsed = time.time() - start_time
    print(f"Gallery build completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
