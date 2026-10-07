import PhotoSwipeLightbox from 'https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe-lightbox.esm.js';
import { gallerySections } from './images.js';

let lightbox = null;

function initGallery() {
  const container = document.getElementById('gallery-container');
  const navContainer = document.getElementById('folder-nav');

  if (!container || !navContainer) return;

  renderFolderNav(navContainer);
  renderGallerySections(container);
  initLightbox();
}

function renderFolderNav(navContainer) {
  const fragment = document.createDocumentFragment();

  const allBtn = document.createElement('button');
  allBtn.className = 'folder-btn active';
  allBtn.textContent = 'All';
  allBtn.dataset.target = 'all';
  allBtn.addEventListener('click', (e) => handleNavClick(e, 'all'));
  fragment.appendChild(allBtn);

  gallerySections.forEach((section, index) => {
    const btn = document.createElement('button');
    btn.className = 'folder-btn';
    btn.textContent = section.title;
    btn.dataset.target = `section-${index}`;
    btn.addEventListener('click', (e) => handleNavClick(e, `section-${index}`));
    fragment.appendChild(btn);
  });

  navContainer.appendChild(fragment);
}

function handleNavClick(event, targetId) {
  document.querySelectorAll('.folder-btn').forEach((btn) => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');

  if (targetId === 'all') {
    document.querySelectorAll('.gallery-section').forEach((sec) => {
      sec.style.display = 'block';
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      document.querySelectorAll('.gallery-section').forEach((sec) => {
        sec.style.display = sec.id === targetId ? 'block' : 'none';
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  event.currentTarget.scrollIntoView({
    behavior: 'smooth',
    block: 'nearest',
    inline: 'center'
  });
}

function renderGallerySections(container) {
  const fragment = document.createDocumentFragment();

  gallerySections.forEach((section, index) => {
    const sectionEl = document.createElement('section');
    sectionEl.className = 'gallery-section';
    sectionEl.id = `section-${index}`;

    // Base paths for photos and thumbs in this section
    const isRoot = section.path === '.';
    const photoBasePath = isRoot ? './photos' : `./photos/${section.path}`;
    const thumbBasePath = isRoot ? './thumbs' : `./thumbs/${section.path}`;

    const itemsHTML = section.items
      .map(([filename, width, height]) => {
        const src = `${photoBasePath}/${filename}`;
        const thumb = `${thumbBasePath}/${filename}`;

        // Derive clean alt text from filename dynamically
        const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
        const alt = nameWithoutExt.replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();

        return `
          <a 
            href="${src}" 
            data-pswp-width="${width}" 
            data-pswp-height="${height}" 
            target="_blank"
            rel="noreferrer"
          >
            <img 
              src="${thumb}" 
              alt="${alt}" 
              loading="lazy" 
              decoding="async"
            />
          </a>
        `;
      })
      .join('');

    sectionEl.innerHTML = `
      <h2 class="section-title">${section.title}</h2>
      <div class="insta-grid">${itemsHTML}</div>
    `;

    fragment.appendChild(sectionEl);
  });

  container.appendChild(fragment);
}

function initLightbox() {
  if (lightbox) {
    lightbox.destroy();
  }

  lightbox = new PhotoSwipeLightbox({
    gallery: '#gallery-container',
    children: '.insta-grid a',
    pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe.esm.js'),
    bgOpacity: 0.95,
    showHideAnimationType: 'zoom'
  });

  lightbox.init();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initGallery);
} else {
  initGallery();
}
