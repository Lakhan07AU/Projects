/**
 * particles.js — Star field, fireflies, confetti, fireworks, rain
 */
window.Particles = (function () {
  'use strict';

  const content = window.BIRTHDAY_CONTENT || {};

  /* ── Star Field (Intro) ── */
  function initStars() {
    const container = document.getElementById('starField');
    if (!container) return;
    const count = content.starCount || 150;

    for (let i = 0; i < count; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      const size  = Math.random() * 2.5 + 0.5;
      const dur   = (Math.random() * 4 + 2).toFixed(1);
      const delay = (Math.random() * 6).toFixed(1);
      star.style.cssText = `
        left:${Math.random()*100}%;
        top:${Math.random()*100}%;
        width:${size}px;
        height:${size}px;
        --dur:${dur}s;
        --delay:${delay}s;
      `;
      container.appendChild(star);
    }
  }

  /* ── Fireflies (Intro canvas) ── */
  function initFireflies() {
    const count = content.fireflyCount || 20;
    const intro = document.getElementById('section-intro');
    if (!intro) return;

    for (let i = 0; i < count; i++) {
      const ff = document.createElement('div');
      ff.className = 'firefly';
      ff.setAttribute('aria-hidden', 'true');
      const dur   = (Math.random() * 6 + 5).toFixed(1);
      const delay = (Math.random() * 8).toFixed(1);
      const tx1   = (Math.random() * 120 - 60).toFixed(0);
      const ty1   = (Math.random() * 80  - 40).toFixed(0);
      const tx2   = (Math.random() * 120 - 60).toFixed(0);
      const ty2   = (Math.random() * 80  - 40).toFixed(0);
      const tx3   = (Math.random() * 80  - 40).toFixed(0);
      const ty3   = (Math.random() * 60  - 30).toFixed(0);
      ff.style.cssText = `
        left:${Math.random()*100}%;
        top:${Math.random()*100}%;
        --dur:${dur}s; --delay:${delay}s;
        --tx1:${tx1}px; --ty1:${ty1}px;
        --tx2:${tx2}px; --ty2:${ty2}px;
        --tx3:${tx3}px; --ty3:${ty3}px;
      `;
      intro.appendChild(ff);
    }
  }

  /* ── Falling Leaves (Loneliness) ── */
  function initLeaves() {
    const wrap = document.getElementById('leavesWrap');
    if (!wrap) return;
    const leaves = content.leaves || ['🍂','🍁','🍃'];

    for (let i = 0; i < 18; i++) {
      const leaf  = document.createElement('span');
      leaf.className = 'falling-leaf';
      leaf.setAttribute('aria-hidden','true');
      leaf.textContent = leaves[i % leaves.length];
      const dur   = (Math.random() * 8 + 6).toFixed(1);
      const delay = (Math.random() * 12).toFixed(1);
      const drift = (Math.random() * 200 - 100).toFixed(0);
      const size  = (Math.random() * 10 + 14).toFixed(0);
      leaf.style.cssText = `
        left:${Math.random()*100}%;
        --dur:${dur}s; --delay:${delay}s;
        --drift:${drift}px; --size:${size}px;
      `;
      wrap.appendChild(leaf);
    }
  }

  /* ── Floating Hearts (Family) ── */
  function initHearts() {
    const wrap = document.getElementById('heartsWrap');
    if (!wrap) return;

    for (let i = 0; i < 14; i++) {
      const h   = document.createElement('span');
      h.className = 'floating-heart';
      h.setAttribute('aria-hidden','true');
      h.textContent = ['❤️','💕','💖','🌸','✨'][i % 5];
      const dur   = (Math.random() * 5 + 5).toFixed(1);
      const delay = (Math.random() * 10).toFixed(1);
      const size  = (Math.random() * 14 + 14).toFixed(0);
      h.style.cssText = `
        left:${Math.random()*100}%;
        bottom:${Math.random()*30}%;
        --dur:${dur}s; --delay:${delay}s; --size:${size}px;
      `;
      wrap.appendChild(h);
    }
  }

  /* ── Fairy Lights String (Family) ── */
  function initFairyLights() {
    const string = document.getElementById('fairyLights');
    if (!string) return;
    const colors = ['#ff6b6b','#ffd700','#98fb98','#87ceeb','#dda0dd','#ffa500'];
    const count  = 30;

    for (let i = 0; i < count; i++) {
      const bulb = document.createElement('div');
      bulb.className = 'fairy-light';
      bulb.setAttribute('aria-hidden','true');
      const color = colors[i % colors.length];
      const dur   = (Math.random() * 2 + 1.5).toFixed(1);
      const delay = (Math.random() * 3).toFixed(1);
      bulb.style.cssText = `
        left:${(i / count) * 100}%;
        color:${color};
        background:${color};
        box-shadow:0 0 6px 2px ${color};
        --dur:${dur}s; --delay:${delay}s;
      `;
      string.appendChild(bulb);
    }
  }

  /* ── Rain (Struggle section) ── */
  function initRain() {
    const container = document.getElementById('rainContainer');
    if (!container) return;

    for (let i = 0; i < 80; i++) {
      const drop = document.createElement('div');
      drop.className = 'raindrop';
      drop.setAttribute('aria-hidden','true');
      const dur    = (Math.random() * 0.6 + 0.5).toFixed(2);
      const delay  = (Math.random() * 2).toFixed(2);
      const height = (Math.random() * 20 + 10).toFixed(0);
      drop.style.cssText = `
        left:${Math.random()*100}%;
        height:${height}px;
        --dur:${dur}s; --delay:${delay}s;
      `;
      container.appendChild(drop);
    }

    // Rain streaks on window glass
    const glass = document.getElementById('rainGlass');
    if (!glass) return;
    for (let i = 0; i < 14; i++) {
      const streak = document.createElement('div');
      streak.className = 'rain-streak';
      streak.setAttribute('aria-hidden','true');
      const dur    = (Math.random() * 3 + 2).toFixed(1);
      const delay  = (Math.random() * 4).toFixed(1);
      const height = (Math.random() * 40 + 30).toFixed(0);
      streak.style.cssText = `
        left:${5 + Math.random()*85}%;
        height:${height}px;
        --dur:${dur}s; --delay:${delay}s;
      `;
      glass.appendChild(streak);
    }
  }

  /* ── Particle canvas (Gifts / Wishes bg) ── */
  function initCanvas(canvasId, particleColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];

    function resize() {
      W = canvas.width  = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 60; i++) {
      particles.push({
        x:  Math.random() * (W || 800),
        y:  Math.random() * (H || 600),
        r:  Math.random() * 2 + 0.5,
        dx: (Math.random() - 0.5) * 0.4,
        dy: (Math.random() - 0.5) * 0.4,
        a:  Math.random(),
      });
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = particleColor || 'rgba(255,255,255,0.5)';
        ctx.globalAlpha = p.a * 0.6;
        ctx.fill();
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0 || p.x > W) p.dx *= -1;
        if (p.y < 0 || p.y > H) p.dy *= -1;
        p.a += (Math.random() - 0.5) * 0.05;
        p.a  = Math.max(0.1, Math.min(1, p.a));
      });
      ctx.globalAlpha = 1;
      requestAnimationFrame(draw);
    }
    draw();
  }

  /* ── Confetti Burst ── */
  function launchConfetti(count = 120) {
    const colors = ['#f43f5e','#9333ea','#f59e0b','#10b981','#3b82f6','#ec4899','#fbbf24'];
    for (let i = 0; i < count; i++) {
      const piece = document.createElement('div');
      piece.className = 'confetti-piece';
      const size  = Math.random() * 10 + 6;
      const color = colors[Math.floor(Math.random() * colors.length)];
      const dur   = (Math.random() * 3 + 3).toFixed(1);
      const delay = (Math.random() * 2).toFixed(2);
      const drift = ((Math.random() - 0.5) * 300).toFixed(0);
      piece.style.cssText = `
        left:${Math.random()*100}%;
        width:${size}px;
        height:${size * (Math.random() > 0.5 ? 1 : 2)}px;
        background:${color};
        --dur:${dur}s; --delay:${delay}s; --drift:${drift}px;
        transform:rotate(${Math.random()*360}deg);
      `;
      document.body.appendChild(piece);
      setTimeout(() => piece.remove(), (parseFloat(dur) + parseFloat(delay) + 1) * 1000);
    }
  }

  /* ── Fireworks ── */
  function launchFirework(x, y) {
    const colors = ['#f43f5e','#9333ea','#f59e0b','#10b981','#fbbf24','#fb7185'];
    const sparkCount = 20;

    for (let i = 0; i < sparkCount; i++) {
      const angle  = (i / sparkCount) * Math.PI * 2;
      const dist   = Math.random() * 80 + 40;
      const endX   = x + Math.cos(angle) * dist;
      const endY   = y + Math.sin(angle) * dist;
      const spark  = document.createElement('div');
      const color  = colors[Math.floor(Math.random() * colors.length)];
      const size   = Math.random() * 5 + 3;

      spark.style.cssText = `
        position:fixed;
        left:${x}px; top:${y}px;
        width:${size}px; height:${size}px;
        background:${color};
        border-radius:50%;
        pointer-events:none;
        z-index:3000;
        box-shadow:0 0 6px 2px ${color};
        transition: left 0.8s ease-out, top 0.8s ease-out, opacity 0.8s ease-out;
      `;
      document.body.appendChild(spark);

      requestAnimationFrame(() => {
        spark.style.left    = endX + 'px';
        spark.style.top     = endY + 'px';
        spark.style.opacity = '0';
      });

      setTimeout(() => spark.remove(), 900);
    }
  }

  function autoFireworks() {
    const positions = [
      [20, 20],[80, 15],[50, 30],[15, 50],[85, 45],
      [35, 20],[65, 35],[10, 30],[90, 60],[50, 15],
    ];
    positions.forEach((p, i) => {
      setTimeout(() => {
        const x = window.innerWidth  * (p[0] / 100);
        const y = window.innerHeight * (p[1] / 100);
        launchFirework(x, y);
      }, i * 300);
    });
  }

  /* ── Click-anywhere fireworks on final page ── */
  function enableClickFireworks() {
    const final = document.getElementById('section-final');
    if (!final) return;
    final.addEventListener('click', (e) => {
      launchFirework(e.clientX, e.clientY);
    });
  }

  /* ── Init All ── */
  function init() {
    initStars();
    initFireflies();
    initLeaves();
    initHearts();
    initFairyLights();
    initRain();
    initCanvas('giftsCanvas',  'rgba(147,51,234,0.7)');
    initCanvas('wishesCanvas', 'rgba(244,63,94,0.6)');
    enableClickFireworks();
  }

  return { init, launchConfetti, launchFirework, autoFireworks };
})();
