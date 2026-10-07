FROM nginx:alpine

# Force Python stdout/stderr streams to be unbuffered
ENV PYTHONUNBUFFERED=1

# Install Python3 and Pillow dependencies
RUN apk add --no-cache python3 py3-pillow

WORKDIR /usr/share/nginx/html

# Clear default Nginx web root
RUN rm -rf ./*

# Copy app code and scripts
COPY index.htm main.js ./
COPY generate_gallery.py /app/generate_gallery.py
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# 1. Symlink root /input directly to /usr/share/nginx/html/photos
# 2. Create internal writeable /tmp/thumbs directory and symlink it to /usr/share/nginx/html/thumbs
RUN mkdir -p /tmp/thumbs && \
    ln -s /input /usr/share/nginx/html/photos && \
    ln -s /tmp/thumbs /usr/share/nginx/html/thumbs

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
