FROM nginx:alpine

# Install Python3 and Pillow dependencies
RUN apk add --no-cache python3 py3-pillow

WORKDIR /usr/share/nginx/html

# Clear default Nginx web root
RUN rm -rf ./*

# Copy app code and scripts
COPY index.htm main.js ./
COPY generate_gallery.py /app/generate_gallery.py
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]