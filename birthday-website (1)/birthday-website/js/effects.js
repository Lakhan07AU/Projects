/**
 * effects.js — GSAP scroll animations, section transitions, section observers
 */
window.Effects = (function () {
  'use strict';

  /* ── Intersection Observer for .reveal elements ── */
  function initReveal() {
    const items = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, idx) => {
        if (entry.isIntersecting) {
          // Stagger siblings a little
          const delay = parseFloat(entry.target.style.getPropertyValue('--delay') || 0) * 1000;
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, delay || idx * 80);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    items.forEach(item => observer.observe(item));
  }

  /* ── School timeline items ── */
  function initTimeline() {
    const items = document.querySelectorAll('.timeline-item');
    if (!items.length) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('visible'), i * 150);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    items.forEach(item => observer.observe(item));
  }

  /* ── Section observer — track active section for nav dots & audio ── */
  function initSectionObserver() {
    const sections  = document.querySelectorAll('[data-section]');
    const navDots   = document.querySelectorAll('.nav-dot');
    const navWrap   = document.getElementById('nav-dots');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const idx = entry.target.dataset.section;

        // Update nav dots
        navDots.forEach((dot, i) => dot.classList.toggle('active', i === parseInt(idx)));

        // Show nav dots after intro
        if (parseInt(idx) > 0 && navWrap) navWrap.classList.add('visible');

        // Change audio track
        const audioKey = entry.target.dataset.audio;
        if (audioKey && window.AudioManager) {
          window.AudioManager.play(audioKey);
        }

        // Thunder flash only for struggle section
        const thunder = document.getElementById('thunderFlash');
        if (thunder) {
          thunder.style.display = (entry.target.id === 'section-struggle') ? 'block' : 'none';
        }
      });
    }, { threshold: 0.4 });

    sections.forEach(s => observer.observe(s));
  }

  /* ── GSAP page-level animations (if GSAP loaded) ── */
  function initGSAP() {
    if (typeof gsap === 'undefined') return;
    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);
    }

    // Parallax on intro headline
    const headline = document.querySelector('.intro-headline');
    if (headline && typeof ScrollTrigger !== 'undefined') {
      gsap.to(headline, {
        yPercent: -30,
        opacity: 0,
        ease: 'none',
        scrollTrigger: {
          trigger: '#section-intro',
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        }
      });
    }

    // Parallax moon (loneliness)
    const moon = document.querySelector('.lone-moon');
    if (moon && typeof ScrollTrigger !== 'undefined') {
      gsap.to(moon, {
        yPercent: 20,
        ease: 'none',
        scrollTrigger: {
          trigger: '#section-loneliness',
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        }
      });
    }

    // Success grid cards stagger
    const achievementCards = document.querySelectorAll('.achievement-card');
    if (achievementCards.length && typeof ScrollTrigger !== 'undefined') {
      gsap.from(achievementCards, {
        y: 50,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.success-grid',
          start: 'top 80%',
        }
      });
    }

    // Polaroid swing animation with GSAP
    document.querySelectorAll('.photo-rope-wrap').forEach((item, i) => {
      gsap.to(item, {
        rotation: (i % 2 === 0 ? 4 : -4),
        duration: 2 + i * 0.3,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        transformOrigin: 'top center',
      });
    });
  }

  /* ── Smooth scroll for nav dots ── */
  function initSmoothScroll() {
    document.querySelectorAll('.nav-dot').forEach(dot => {
      dot.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(dot.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ── Loneliness text word-by-word reveal ── */
  function initLoneTextReveal() {
    const el = document.getElementById('loneText');
    if (!el) return;

    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        el.classList.add('visible');
        const text  = el.innerHTML;
        const words = text.split(/(\s+|<br\/>)/);
        el.innerHTML = words
          .map((w, i) => w.match(/^\s+$/) || w === '<br/>'
            ? w
            : `<span style="transition-delay:${i * 60}ms">${w}</span>`)
          .join('');

        // Trigger
        setTimeout(() => {
          el.querySelectorAll('span').forEach((s, i) => {
            setTimeout(() => { s.style.opacity = '1'; s.style.transform = 'translateY(0)'; }, i * 60);
          });
        }, 300);

        // Set initial state
        el.querySelectorAll('span').forEach(s => {
          s.style.opacity   = '0';
          s.style.transform = 'translateY(12px)';
          s.style.display   = 'inline-block';
          s.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        });

        observer.disconnect();
      }
    }, { threshold: 0.5 });

    observer.observe(el);
  }

  /* ── Init ── */
  function init() {
    initReveal();
    initTimeline();
    initSectionObserver();
    initSmoothScroll();
    initLoneTextReveal();
    // Defer GSAP init slightly so GSAP script has loaded
    requestAnimationFrame(() => setTimeout(initGSAP, 100));
  }

  return { init };
})();
