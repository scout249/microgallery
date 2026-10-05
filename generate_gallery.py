import os
from pathlib import Path
from PIL import Image

# Directories
PHOTOS_DIR = Path("./photos")
THUMBS_DIR = Path("./thumbs")
OUTPUT_JS = Path("./images.js")

# Thumbnail target dimensions (max width/height)
THUMB_MAX_SIZE = (400, 400)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def process_gallery():
    if not PHOTOS_DIR.exists():
        print(f"Directory '{PHOTOS_DIR}' does not exist.")
        return

    sections = []

    # Iterate through subdirectories in ./photos
    # Top-level images in ./photos will be grouped under "General"
    subdirs = [d for d in PHOTOS_DIR.iterdir() if d.is_dir()]
    if not subdirs:
        subdirs = [PHOTOS_DIR]

    for subdir in sorted(subdirs):
        section_title = subdir.name if subdir != PHOTOS_DIR else "General"
        items = []

        # Find all valid image files
        image_files = [f for f in subdir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
        
        for img_path in sorted(image_files):
            try:
                with Image.open(img_path) as img:
                    orig_width, orig_height = img.size

                    # Create corresponding thumbnail path maintaining subfolder structure
                    relative_path = img_path.relative_to(PHOTOS_DIR)
                    thumb_path = THUMBS_DIR / relative_path
                    thumb_path.parent.mkdir(parents=True, exist_ok=True)

                    # Save optimized thumbnail
                    img.thumbnail(THUMB_MAX_SIZE, Image.Resampling.LANCZOS)
                    img.save(thumb_path, optimize=True, quality=80)

                    # Record metadata relative to index.htm
                    items.append({
                        "src": f"./{img_path.as_posix()}",
                        "thumb": f"./{thumb_path.as_posix()}",
                        "width": orig_width,
                        "height": orig_height,
                        "alt": img_path.stem.replace("-", " ").replace("_", " ").title()
                    })
                    print(f"Processed: {relative_path}")

            except Exception as e:
                print(f"Skipping {img_path}: {e}")

        if items:
            sections.append({
                "title": section_title,
                "items": items
            })

    # Write output to images.js formatted as ES module
    import json
    js_content = f"export const gallerySections = {json.dumps(sections, indent=2)};\n"
    OUTPUT_JS.write_text(js_content, encoding="utf-8")

    print(f"\nDone! Generated thumbnails in '{THUMBS_DIR}' and updated '{OUTPUT_JS}'.")

if __name__ == "__main__":
    process_gallery()