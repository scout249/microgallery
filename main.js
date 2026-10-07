import PhotoSwipeLightbox from 'https://cdn.jsdelivr.net/npm/photoswipe@5/dist/photoswipe-lightbox.esm.js';
import { gallerySections } from './images.js';

let lightbox = null;

function initGallery() {
  const container = document.getElementById('gallery-container');
  const mobileNav = document.getElementById('folder-nav-mobile');
  const desktopNav = document.getElementById('folder-nav-desktop');

  if (!container) return;

  if (mobileNav) renderFolderNav(mobileNav);
  if (desktopNav) renderFolderNav(desktopNav);

  renderGallerySections(container);
  initLightbox();
}

function renderFolderNav(navContainer) {
  const fragment = document.createDocumentFragment();

  // Total library photo count
  const totalPhotos = gallerySections.reduce((acc, sec) => acc + (sec.items ? sec.items.length : 0), 0);

  // 'All' Filter Button
  const allBtn = document.createElement('button');
  allBtn.className = 'folder-btn active';
  allBtn.dataset.target = 'all';
  allBtn.innerHTML = `<span>All Photos</span><span class="count">${totalPhotos}</span>`;
  allBtn.addEventListener('click', (e) => handleNavClick(e, 'all'));
  fragment.appendChild(allBtn);

  // Folder Buttons
  gallerySections.forEach((section, index) => {
    const btn = document.createElement('button');
    btn.className = 'folder-btn';
    btn.dataset.target = `section-${index}`;
    const count = section.items ? section.items.length : 0;
    btn.innerHTML = `<span>${section.title}</span><span class="count">${count}</span>`;
    btn.addEventListener('click', (e) => handleNavClick(e, `section-${index}`));
    fragment.appendChild(btn);
  });

  navContainer.appendChild(fragment);
}

function handleNavClick(event, targetId) {
  document.querySelectorAll('.folder-btn').forEach((btn) => {
    if (btn.dataset.target === targetId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  if (targetId === 'all') {
    document.querySelectorAll('.gallery-section').forEach((sec) => {
      sec.style.display = 'block';
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    document.querySelectorAll('.gallery-section').forEach((sec) => {
      sec.style.display = sec.id === targetId ? 'block' : 'none';
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

    const isRoot = section.path === '.';
    const photoBasePath = isRoot ? './photos' : `./photos/${section.path}`;
    const thumbBasePath = isRoot ? './thumbs' : `./thumbs/${section.path}`;

    const itemCount = section.items ? section.items.length : 0;

    const itemsHTML = section.items
      .map(([filename, width, height]) => {
        const src = `${photoBasePath}/${filename}`;
        const thumb = `${thumbBasePath}/${filename}`;

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
              onload="this.classList.add('loaded')"
            />
          </a>
        `;
      })
      .join('');

    sectionEl.innerHTML = `
      <div class="section-header">
        <h2 class="section-title">${section.title}</h2>
        <span class="section-meta">${itemCount} photos</span>
      </div>
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
    bgOpacity: 0.96,
    showHideAnimationType: 'zoom'
  });

  lightbox.init();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initGallery);
} else {
  initGallery();
}
