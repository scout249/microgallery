import PhotoSwipeLightbox from 'https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe-lightbox.esm.js';
import { gallerySections } from './images.js';

function renderGallery() {
  const container = document.getElementById('gallery-container');
  if (!container) return;

  const fragment = document.createDocumentFragment();

  gallerySections.forEach((section) => {
    const sectionEl = document.createElement('section');
    sectionEl.className = 'gallery-section';

    const itemsHTML = section.items
      .map((item) => {
        // Strictly use thumb for grid img, falling back to src if thumb is omitted
        const thumbnailUrl = item.thumb || item.src;

        return `
          <a 
            href="${item.src}" 
            data-pswp-width="${item.width}" 
            data-pswp-height="${item.height}" 
            target="_blank"
            rel="noreferrer"
          >
            <img 
              src="${thumbnailUrl}" 
              alt="${item.alt}" 
              width="400" 
              height="300" 
              loading="lazy" 
              decoding="async"
            />
          </a>
        `;
      })
      .join('');

    sectionEl.innerHTML = `
      <h2 class="section-title">${section.title}</h2>
      <div class="adaptive-grid">${itemsHTML}</div>
    `;

    fragment.appendChild(sectionEl);
  });

  container.appendChild(fragment);

  // Initialize PhotoSwipe Lightbox
  const lightbox = new PhotoSwipeLightbox({
    gallery: '#gallery-container',
    children: '.adaptive-grid a',
    pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe.esm.js')
  });

  lightbox.init();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', renderGallery);
} else {
  renderGallery();
}