# MicroGallery

An ultra-lightweight, zero-database static photo gallery container powered by **Nginx (Alpine)**, **Python 3 (Pillow)**, and **PhotoSwipe v5**. 

On container startup, an automated Python background worker scans your high-resolution photos, extracts image dimensions/EXIF metadata, generates lightweight WebP thumbnails, and serves a responsive, lightning-fast gallery grid.

---

## Features

- **Zero-Database:** No MySQL, PostgreSQL, or persistent database required.
- **Auto-Generated Thumbnails:** Automatically creates optimized thumbnails for new photos on startup.
- **Ultra-Fast & Lightweight:** Built on Nginx Alpine with minimal CPU/RAM footprint (~50MB).
- **Responsive Lightbox:** Full-resolution viewing with zoom and touch-gesture support via PhotoSwipe v5.
- **Multi-Architecture:** Supports `linux/amd64` and `linux/arm64` (Synology NAS, Raspberry Pi, Cloud VPS).

---

## 1. Directory Setup & Adding Photos

Before launching the container, create the host directory layout and copy your photos into the `photos` directory.

### Create the Photos Directory
Run the following command on your host terminal (or create the folders via your NAS file manager):

```bash
mkdir -p photos
```

### Organize Your Images
Place your images inside the `photos` directory. You can organize photos into subfolders—`microgallery` will automatically group images by folder names:

```text
microgallery/
├── docker-compose.yml
└── photos/
    ├── Paris/
    │   ├── IMG_001.jpg
    │   └── IMG_002.jpg
    ├── Morocco/
    │   └── IMG_003.jpg
    └── photo_root.jpg
```

### Set File Permissions
Ensure the Docker daemon and container have read access to your photos:

```bash
chmod -R 755 photos
```

---

## 2. Docker Compose File Breakdown

Below is the recommended `docker-compose.yml` configuration:

```yaml
version: '3.8'

services:
  gallery:
    image: scout249/microgallery:latest
    container_name: microgallery
    ports:
      - "8080:80"
    volumes:
      - ./photos:/usr/share/nginx/html/photos:ro
    restart: unless-stopped
```

### Parameter Explanation

| Key | Description |
| :--- | :--- |
| `image` | Specifies the multi-arch Docker Hub image (`amd64` / `arm64`). |
| `container_name` | Sets a clean name (`microgallery`) for easier logging and container management. |
| `ports: "8080:80"` | Maps port `8080` on your host machine to port `80` (Nginx) inside the container. |
| `volumes: ./photos:...:ro` | **Host Bind-Mount:** Mounts your host's `./photos` directory into Nginx's web root as **Read-Only (`:ro`)**, guaranteeing the container never alters or deletes your original high-res photo files. |
| `restart: unless-stopped` | Ensures the gallery automatically restarts if your NAS or server reboots. |

---

## 3. How to Run

You can launch `microgallery` using either **Docker Compose** (recommended) or the **Docker CLI**.

### Option A: Using Docker Compose (Recommended)

1. Save the YAML snippet above as `docker-compose.yml` in your project folder.
2. Start the gallery in detached mode:
   ```bash
   docker compose up -d
   ```
3. Check execution logs to verify thumbnail generation:
   ```bash
   docker compose logs -f gallery
   ```

To stop the container:
```bash
docker compose down
```

---

### Option B: Using `docker run` CLI

1. If you prefer running a single CLI command without `docker-compose.yml`:

```bash
docker run -d \
  --name microgallery \
  -p 8080:80 \
  -v $(pwd):/input:ro \
  --restart unless-stopped \
  scout249/microgallery
```

2. Check execution logs to verify thumbnail generation:
   ```bash
   docker logs -f microgallery
   ```

---

## Accessing Your Gallery

Once the container finishes generating thumbnails, open your web browser and navigate to:

```text
http://<your-server-ip>:8080
```
