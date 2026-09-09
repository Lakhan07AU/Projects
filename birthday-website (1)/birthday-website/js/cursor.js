/**
 * cursor.js — Custom heart cursor (fixed & reliable)
 * - Dot follows mouse exactly, ring lags smoothly behind
 * - Glows pink, turns gold on hover, pulses on click
 * - Spawns floating hearts on every click
 */
(function () {
  'use strict';

  // Only run on non-touch desktop
  if (window.matchMedia('(max-width: 768px)').matches) return;
  if ('ontouchstart' in window) return;

  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;

  // Start both off-screen so they don't flash at (0,0)
  let mouseX = -200, mouseY = -200;
  let ringX  = -200, ringY  = -200;
  let isVisible = false;

  // Apply positions directly — no CSS transition on left/top (use transform instead)
  function setPos(el, x, y) {
    el.style.left = x + 'px';
    el.style.top  = y + 'px';
  }

  // Smooth ring follow via RAF
  function tick() {
    ringX += (mouseX - ringX) * 0.14;
    ringY += (mouseY - ringY) * 0.14;
    setPos(dot,  mouseX, mouseY);
    setPos(ring, ringX,  ringY);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // Track mouse position
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    if (!isVisible) {
      // Snap ring to dot on first move so it doesn't sweep across
      ringX = mouseX;
      ringY = mouseY;
      isVisible = true;
    }
  });

  // Hide when mouse leaves window
  document.addEventListener('mouseleave', () => {
    dot.style.opacity  = '0';
    ring.style.opacity = '0';
  });
  document.addEventListener('mouseenter', () => {
    dot.style.opacity  = '1';
    ring.style.opacity = '1';
  });

  // Hover: interactive elements turn cursor gold + bigger
  const hoverSel = 'a, button, [role="button"], [tabindex="0"], .photo-polaroid, .photo-item, .festival-card, .gift-item, .wish-card, .family-photo-item, .nav-dot, .achievement-card, .theater-btn, .audio-btn';

  document.addEventListener('mouseover', (e) => {
    if (e.target.closest(hoverSel)) {
      document.body.classList.add('hovering');
    }
  });
  document.addEventListener('mouseout', (e) => {
    if (e.target.closest(hoverSel)) {
      document.body.classList.remove('hovering');
    }
  });

  // Click: shrink + spawn heart
  document.addEventListener('mousedown', () => {
    document.body.classList.add('clicking');
  });
  document.addEventListener('mouseup', () => {
    document.body.classList.remove('clicking');
  });

  document.addEventListener('click', (e) => {
    spawnHeart(e.clientX, e.clientY);
  });

  // Spawn floating emoji on click
  const heartEmojis = ['❤️','💕','💖','💗','💓','🌸','✨'];
  function spawnHeart(x, y) {
    const el = document.createElement('div');
    el.textContent = heartEmojis[Math.floor(Math.random() * heartEmojis.length)];
    el.setAttribute('aria-hidden', 'true');
    el.style.cssText = `
      position: fixed;
      left: ${x}px;
      top: ${y}px;
      font-size: ${14 + Math.random() * 16}px;
      pointer-events: none;
      user-select: none;
      z-index: 99999;
      transform: translate(-50%, -50%);
      animation: _heartRise 1.1s ease-out forwards;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1150);
  }

  // Inject keyframe once
  if (!document.getElementById('_cursorKF')) {
    const s = document.createElement('style');
    s.id = '_cursorKF';
    s.textContent = `
      @keyframes _heartRise {
        0%   { opacity: 1; transform: translate(-50%, -50%) scale(0.4); }
        100% { opacity: 0; transform: translate(-50%, calc(-50% - 70px)) scale(1.2); }
      }
    `;
    document.head.appendChild(s);
  }

})();
