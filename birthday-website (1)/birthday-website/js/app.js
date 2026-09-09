/**
 * app.js — Main bootstrap: preloader, init sequence, orchestration
 */
(function () {
  'use strict';

  /* ── Preloader ── */
  function runPreloader(onComplete) {
    const bar   = document.getElementById('preloaderBar');
    const count = document.getElementById('preloaderCount');
    const wrap  = document.getElementById('preloader');

    let progress = 0;
    const interval = setInterval(() => {
      // Ease towards 100
      const step = Math.random() * 8 + 2;
      progress = Math.min(progress + step, 100);

      if (bar)   bar.style.width = progress + '%';
      if (count) count.textContent = Math.floor(progress) + '%';

      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          if (wrap) wrap.classList.add('hidden');
          document.body.classList.remove('page-loading');
          onComplete && onComplete();
        }, 600);
      }
    }, 80);
  }

  /* ── Full init ── */
  function initApp() {
    // Order matters: particles first (they inject DOM elements), then effects, then interactions
    window.Particles    && window.Particles.init();
    window.Effects      && window.Effects.init();
    window.Gallery      && window.Gallery.init();
    window.Interactions && window.Interactions.init();

    // Show nav dots
    setTimeout(() => {
      const nav = document.getElementById('nav-dots');
      // Only show after user scrolls past intro
      window.addEventListener('scroll', () => {
        if (window.scrollY > window.innerHeight * 0.5) {
          nav && nav.classList.add('visible');
        }
      }, { passive: true });
    }, 1000);

    // Enable audio on first user interaction
    const firstTouch = () => {
      window.AudioManager && window.AudioManager.enableAudio();
      document.removeEventListener('click',     firstTouch);
      document.removeEventListener('touchstart', firstTouch);
      document.removeEventListener('keydown',   firstTouch);
    };
    document.addEventListener('click',     firstTouch, { once: true });
    document.addEventListener('touchstart', firstTouch, { once: true, passive: true });
    document.addEventListener('keydown',   firstTouch, { once: true });
  }

  /* ── DOM Ready ── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      runPreloader(initApp);
    });
  } else {
    runPreloader(initApp);
  }

})();
