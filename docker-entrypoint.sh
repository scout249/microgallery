#!/bin/sh
set -e

echo "==> Running thumbnail generator..."
python3 /app/generate_gallery.py

echo "==> Starting Nginx..."
exec "$@"