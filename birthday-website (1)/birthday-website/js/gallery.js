/**
 * gallery.js — Lightbox, photo interactions, video theater
 */
window.Gallery = (function () {
  'use strict';

  let currentImages = [];
  let currentIndex  = 0;

  const lightbox  = document.getElementById('lightbox');
  const lbImg     = document.getElementById('lightboxImg');
  const lbCaption = document.getElementById('lightboxCaption');
  const lbClose   = document.getElementById('lightboxClose');
  const lbPrev    = document.getElementById('lightboxPrev');
  const lbNext    = document.getElementById('lightboxNext');

  /* ── Collect all lightbox-enabled images ── */
  function initLightbox() {
    if (!lightbox) return;

    // Gather all lightbox targets
    document.querySelectorAll('[data-lightbox]').forEach(el => {
      el.addEventListener('click', () => {
        const src     = el.dataset.src || '';
        const caption = el.dataset.caption || '';

        // Collect siblings in the same section for prev/next
        const section = el.closest('section') || document.body;
        const siblings = Array.from(section.querySelectorAll('[data-lightbox]'));
        currentImages  = siblings.map(s => ({ src: s.dataset.src || '', caption: s.dataset.caption || '' }));
        currentIndex   = siblings.indexOf(el);

        openLightbox(src, caption);
      });

      // Keyboard accessibility
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          el.click();
        }
      });
    });

    // Close
    lbClose && lbClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) closeLightbox();
    });

    // Nav
    lbPrev && lbPrev.addEventListener('click', showPrev);
    lbNext && lbNext.addEventListener('click', showNext);

    // Keyboard
    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape')      closeLightbox();
      if (e.key === 'ArrowLeft')   showPrev();
      if (e.key === 'ArrowRight')  showNext();
    });

    // Touch swipe
    let touchStartX = 0;
    lightbox.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; });
    lightbox.addEventListener('touchend',   (e) => {
      const diff = touchStartX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) diff > 0 ? showNext() : showPrev();
    });
  }

  function openLightbox(src, caption) {
    if (!lightbox || !lbImg) return;

    if (src) {
      lbImg.src = src;
      lbImg.style.display = 'block';
    } else {
      // Show placeholder message when no real photo yet
      lbImg.style.display = 'none';
    }

    if (lbCaption) lbCaption.textContent = caption || '';
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
    document.body.classList.add('lightbox-open');

    // Announce to screen readers
    lightbox.setAttribute('aria-label', caption || 'Photo viewer');
    lbClose && lbClose.focus();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    document.body.classList.remove('lightbox-open');
  }

  function showPrev() {
    if (!currentImages.length) return;
    currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
    const item = currentImages[currentIndex];
    if (lbImg) lbImg.src = item.src;
    if (lbCaption) lbCaption.textContent = item.caption;
  }

  function showNext() {
    if (!currentImages.length) return;
    currentIndex = (currentIndex + 1) % currentImages.length;
    const item = currentImages[currentIndex];
    if (lbImg) lbImg.src = item.src;
    if (lbCaption) lbCaption.textContent = item.caption;
  }

  /* ── Video Theater ── */
  function initTheater() {
    const content    = window.BIRTHDAY_CONTENT || {};
    const videos     = content.videos || [];
    const screen     = document.getElementById('theaterScreen');
    const videoEl    = document.getElementById('theaterVideo');
    const placeholder= document.getElementById('theaterPlaceholder');
    const thumbsWrap = document.getElementById('videoThumbnails');
    const playBtn    = document.getElementById('theaterPlay');
    const prevBtn    = document.getElementById('theaterPrev');
    const nextBtn    = document.getElementById('theaterNext');
    const fsBtn      = document.getElementById('theaterFullscreen');
    const progressBar= document.getElementById('theaterProgressBar');
    const openBtn    = document.getElementById('theaterOpenBtn');
    const wrap       = document.getElementById('theaterWrap');

    if (!screen) return;

    let currentVideo = 0;

    // Open curtains button
    if (openBtn && wrap) {
      openBtn.addEventListener('click', () => {
        wrap.classList.add('curtains-open');
        openBtn.style.display = 'none';
        if (videos.length && videos[0].src) {
          loadVideo(0);
        }
      });
    }

    // Build thumbnails
    if (thumbsWrap) {
      videos.forEach((v, i) => {
        const thumb = document.createElement('div');
        thumb.className = 'video-thumb' + (i === 0 ? ' active' : '');
        thumb.setAttribute('role', 'listitem');
        thumb.setAttribute('aria-label', v.label || `Video ${i+1}`);
        thumb.setAttribute('tabindex', '0');
        thumb.textContent = v.label || `Video ${i + 1}`;
        thumb.addEventListener('click', () => loadVideo(i));
        thumb.addEventListener('keydown', (e) => { if (e.key === 'Enter') loadVideo(i); });
        thumbsWrap.appendChild(thumb);
      });
    }

    function loadVideo(idx) {
      currentVideo = idx;
      const v = videos[idx];
      if (!v || !v.src) return;

      if (videoEl && placeholder) {
        videoEl.src = v.src;
        videoEl.style.display = 'block';
        placeholder.style.display = 'none';
        videoEl.play().catch(() => {});

        // Update thumbnails
        document.querySelectorAll('.video-thumb').forEach((t, i) => {
          t.classList.toggle('active', i === idx);
        });
      }
    }

    // Play/Pause
    if (playBtn && videoEl) {
      playBtn.addEventListener('click', () => {
        if (videoEl.paused) {
          videoEl.play();
          playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
        } else {
          videoEl.pause();
          playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
        }
      });
      videoEl.addEventListener('play',  () => { playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>'; });
      videoEl.addEventListener('pause', () => { playBtn.innerHTML = '<i class="fa-solid fa-play"></i>'; });
    }

    // Progress
    if (progressBar && videoEl) {
      videoEl.addEventListener('timeupdate', () => {
        if (!videoEl.duration) return;
        progressBar.style.width = (videoEl.currentTime / videoEl.duration * 100) + '%';
      });
      videoEl.addEventListener('ended', () => {
        const next = (currentVideo + 1) % videos.length;
        loadVideo(next);
      });
    }

    // Prev / Next
    prevBtn && prevBtn.addEventListener('click', () => {
      loadVideo((currentVideo - 1 + videos.length) % videos.length);
    });
    nextBtn && nextBtn.addEventListener('click', () => {
      loadVideo((currentVideo + 1) % videos.length);
    });

    // Fullscreen
    if (fsBtn && screen) {
      fsBtn.addEventListener('click', () => {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          screen.requestFullscreen && screen.requestFullscreen();
        }
      });
    }
  }

  /* ── Lazy-load images ── */
  function initLazyLoad() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });

    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
  }

  function init() {
    initLightbox();
    initTheater();
    initLazyLoad();
  }

  return { init, openLightbox, closeLightbox };
})();
