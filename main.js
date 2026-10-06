import PhotoSwipeLightbox from 'https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe-lightbox.esm.js';
import { gallerySections } from './images.js';

let lightbox = null;

function initGallery() {
  const container = document.getElementById('gallery-container');
  const navContainer = document.getElementById('folder-nav');

  if (!container || !navContainer) return;

  // Render Top Folder Navigation
  renderFolderNav(navContainer);

  // Render Gallery Content
  renderGallerySections(container);

  // Initialize PhotoSwipe Lightbox
  initLightbox();
}

function renderFolderNav(navContainer) {
  const fragment = document.createDocumentFragment();

  // "All" Tab
  const allBtn = document.createElement('button');
  allBtn.className = 'folder-btn active';
  allBtn.textContent = 'All';
  allBtn.dataset.target = 'all';
  allBtn.addEventListener('click', (e) => handleNavClick(e, 'all'));
  fragment.appendChild(allBtn);

  // Sub-directory Folder Tabs
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
  // Update active pill state
  document.querySelectorAll('.folder-btn').forEach((btn) => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');

  if (targetId === 'all') {
    // Show all sections
    document.querySelectorAll('.gallery-section').forEach((sec) => {
      sec.style.display = 'block';
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    // Filter to selected sub-directory or scroll to it
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      document.querySelectorAll('.gallery-section').forEach((sec) => {
        sec.style.display = sec.id === targetId ? 'block' : 'none';
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // Keep active pill scrolled into view in top bar
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

    const itemsHTML = section.items
      .map((item) => {
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
              alt="${item.alt || ''}" 
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