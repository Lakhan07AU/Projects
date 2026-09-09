/**
 * interactions.js — Door portal, festival modals, secret gifts, final gift
 */
window.Interactions = (function () {
  'use strict';

  const content = window.BIRTHDAY_CONTENT || {};

  /* ════════════════════════════════════════
     THE MAGIC DOOR
     ════════════════════════════════════════ */
  function initDoor() {
    const door    = document.getElementById('magicDoor');
    const btn     = document.getElementById('btnOpenDoor');
    const section = document.getElementById('section-intro');

    function openDoor() {
      if (!door) return;
      door.classList.add('door-open');
      window.AudioManager && window.AudioManager.enableAudio();
      window.AudioManager && window.AudioManager.play('intro');

      // After door opens, scroll to childhood
      setTimeout(() => {
        const childhood = document.getElementById('section-childhood');
        if (childhood) childhood.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 1400);
    }

    door && door.addEventListener('click', openDoor);
    door && door.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openDoor(); }
    });
    btn  && btn.addEventListener('click', openDoor);
  }

  /* ════════════════════════════════════════
     FESTIVAL CARDS & MODAL
     ════════════════════════════════════════ */
  function initFestivals() {
    const modal      = document.getElementById('festivalModal');
    const modalInner = document.getElementById('festivalModalInner');
    const closeBtn   = document.getElementById('festivalModalClose');
    const modalBg    = document.getElementById('festivalModalBg');

    if (!modal) return;

    const festivals = content.festivals || {};

    document.querySelectorAll('[data-festival]').forEach(card => {
      card.addEventListener('click', () => openFestivalModal(card.dataset.festival));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openFestivalModal(card.dataset.festival); }
      });
    });

    function openFestivalModal(key) {
      const f = festivals[key];
      if (!f || !modalInner) return;

      const photos = (f.photos || []).map(p =>
        p.src
          ? `<div class="photo-item" style="cursor:default;" data-lightbox data-src="${p.src}" data-caption="${p.caption || ''}">
               <img src="${p.src}" alt="${p.caption || ''}" loading="lazy" />
             </div>`
          : ''
      ).join('');

      modalInner.innerHTML = `
        <div style="text-align:center; margin-bottom:var(--space-md);">
          <div style="font-size:3rem; margin-bottom:8px;">${f.emoji || '✨'}</div>
          <h2 style="font-family:var(--font-display); font-size:var(--fs-lg); color:${f.color || 'var(--c-champagne)'}; margin-bottom:var(--space-sm);">${f.title}</h2>
          <div class="divider"></div>
          <p style="font-family:var(--font-accent); font-size:var(--fs-md); color:rgba(255,255,255,0.7); line-height:1.9; max-width:560px; margin:0 auto var(--space-md);">${f.memory}</p>
        </div>
        ${photos
          ? `<div class="photo-grid cols-3" style="gap:var(--space-xs);">${photos}</div>`
          : `<div style="text-align:center; color:rgba(255,255,255,0.25); font-size:var(--fs-sm); padding:var(--space-md);">
               📸 Add photos for ${f.title} in data/content.js
             </div>`
        }
      `;

      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
      closeBtn && closeBtn.focus();

      // Re-bind lightbox for newly added images
      modalInner.querySelectorAll('[data-lightbox]').forEach(el => {
        el.style.cursor = 'pointer';
        el.addEventListener('click', () => {
          window.Gallery && window.Gallery.openLightbox(el.dataset.src, el.dataset.caption);
        });
      });
    }

    function closeFestivalModal() {
      modal.classList.remove('open');
      document.body.style.overflow = '';
    }

    closeBtn && closeBtn.addEventListener('click', closeFestivalModal);
    modalBg  && modalBg.addEventListener('click', closeFestivalModal);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('open')) closeFestivalModal();
    });
  }

  /* ════════════════════════════════════════
     SECRET GIFT BOXES
     ════════════════════════════════════════ */
  function initGifts() {
    const popup    = document.getElementById('giftPopup');
    const popupBg  = document.getElementById('giftPopupBg');
    const giftIcon = document.getElementById('giftIcon');
    const giftTitle= document.getElementById('giftTitle');
    const giftText = document.getElementById('giftText');
    const closeBtn = document.getElementById('giftClose');

    if (!popup) return;

    const gifts = content.gifts || [];

    document.querySelectorAll('.gift-item').forEach(item => {
      item.addEventListener('click', () => {
        const idx  = parseInt(item.dataset.gift);
        const gift = gifts[idx];
        const box  = item.querySelector('.gift-box');

        // Open box animation
        if (box) box.classList.add('open');

        setTimeout(() => {
          openGiftPopup(gift || {
            icon:    '🎁',
            title:   'A Surprise',
            message: 'Add your secret gift content in data/content.js ✨',
          });
        }, 500);
      });

      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); item.click(); }
      });
    });

    function openGiftPopup(gift) {
      if (giftIcon)  giftIcon.textContent  = gift.icon    || '🎁';
      if (giftTitle) giftTitle.textContent = gift.title   || 'A Secret';
      if (giftText)  {
        giftText.innerHTML = (gift.message || '').replace(/\n/g, '<br/>');
      }
      popup.classList.add('open');
      document.body.style.overflow = 'hidden';

      // Confetti burst on gift open
      window.Particles && window.Particles.launchConfetti(60);
    }

    function closeGiftPopup() {
      popup.classList.remove('open');
      document.body.style.overflow = '';
      // Reset all gift boxes
      document.querySelectorAll('.gift-box').forEach(box => box.classList.remove('open'));
    }

    closeBtn && closeBtn.addEventListener('click', closeGiftPopup);
    popupBg  && popupBg.addEventListener('click', closeGiftPopup);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && popup.classList.contains('open')) closeGiftPopup();
    });
  }

  /* ════════════════════════════════════════
     FINAL GIFT BOX
     ════════════════════════════════════════ */
  function initFinalGift() {
    const btn     = document.getElementById('btnOpenFinalGift');
    const giftBox = document.getElementById('finalGiftBox');
    const lid     = document.getElementById('finalGiftLid');

    if (!btn && !giftBox) return;

    function triggerFinalGift() {
      // Open lid
      if (lid) lid.style.transform = 'perspective(400px) rotateX(-110deg)';

      // Explosion of particles
      setTimeout(() => {
        window.Particles && window.Particles.launchConfetti(200);
        window.Particles && window.Particles.autoFireworks();

        // Floating hearts explosion
        const emojis = ['❤️','💖','💕','🌸','✨','🎂','🎈','🎊','🌺','💝'];
        for (let i = 0; i < 30; i++) {
          setTimeout(() => {
            const heart    = document.createElement('div');
            heart.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            const cx = window.innerWidth  * 0.5 + (Math.random() - 0.5) * 200;
            const cy = window.innerHeight * 0.5 + (Math.random() - 0.5) * 100;
            heart.style.cssText = `
              position:fixed;
              left:${cx}px; top:${cy}px;
              font-size:${20 + Math.random()*30}px;
              pointer-events:none;
              z-index:4000;
              animation:finalHeartBurst 2s ease-out forwards;
            `;
            document.body.appendChild(heart);
            setTimeout(() => heart.remove(), 2200);
          }, i * 80);
        }

        // Happy Birthday text overlay
        showHappyBirthday();

      }, 400);
    }

    btn      && btn.addEventListener('click', triggerFinalGift);
    giftBox  && giftBox.addEventListener('click', triggerFinalGift);
    giftBox  && giftBox.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); triggerFinalGift(); }
    });

    // Inject burst animation
    if (!document.getElementById('finalBurstKF')) {
      const style = document.createElement('style');
      style.id = 'finalBurstKF';
      style.textContent = `
        @keyframes finalHeartBurst {
          0%   { opacity:1; transform:translate(0,0) scale(0.5) rotate(0deg); }
          100% { opacity:0; transform:translate(${Math.random()>0.5?'':'-'}${50+Math.random()*150}px, -${80+Math.random()*200}px) scale(1.5) rotate(${Math.random()*360}deg); }
        }
        @keyframes happyBdayIn {
          0%   { opacity:0; transform:translate(-50%,-50%) scale(0.5); }
          60%  { opacity:1; transform:translate(-50%,-50%) scale(1.08); }
          100% { opacity:1; transform:translate(-50%,-50%) scale(1); }
        }
      `;
      document.head.appendChild(style);
    }
  }

  function showHappyBirthday() {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position:fixed; inset:0; z-index:5000;
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      background:rgba(0,0,0,0.7); backdrop-filter:blur(10px);
      pointer-events:auto;
    `;
    overlay.innerHTML = `
      <div style="
        position:absolute; top:50%; left:50%;
        text-align:center;
        animation:happyBdayIn 1s var(--ease-out-expo,cubic-bezier(0.16,1,0.3,1)) forwards;
        transform:translate(-50%,-50%);
        width:90vw; max-width:700px;
      ">
        <div style="font-size:clamp(3rem,10vw,7rem); font-family:var(--font-accent,'Dancing Script',cursive); background:linear-gradient(135deg,#f43f5e,#f59e0b,#9333ea); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1.2;">
          Happy Birthday!
        </div>
        <div style="font-size:4rem; margin:16px 0;">🎂✨🎈</div>
        <p style="font-family:var(--font-accent,'Dancing Script',cursive); font-size:clamp(1rem,3vw,1.6rem); color:rgba(255,255,255,0.8); line-height:1.8; max-width:500px; margin:0 auto;">
          ${content.sister?.name ? `Dear ${content.sister.name},` : 'Dear Sister,'}<br/>
          You deserve all the love in this world.<br/>
          <strong style="color:#fbbf24;">We love you. Always. ❤️</strong>
        </p>
        <button onclick="this.closest('div[style]').parentElement.remove()" style="
          margin-top:2rem; padding:12px 32px;
          background:linear-gradient(135deg,#f43f5e,#9333ea);
          border:none; border-radius:999px; color:#fff;
          font-size:1rem; cursor:pointer; font-family:inherit;
          box-shadow:0 8px 40px rgba(244,63,94,0.4);
        ">
          Thank you 💝
        </button>
      </div>
    `;
    document.body.appendChild(overlay);
  }

  /* ════════════════════════════════════════
     INTRO CANVAS (galaxy swirl)
     ════════════════════════════════════════ */
  function initIntroCanvas() {
    const canvas = document.getElementById('introCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H;
    const dots = [];

    function resize() {
      W = canvas.width  = canvas.offsetWidth  || window.innerWidth;
      H = canvas.height = canvas.offsetHeight || window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Generate galaxy spiral dots
    for (let arm = 0; arm < 3; arm++) {
      for (let i = 0; i < 120; i++) {
        const angle  = (i / 120) * Math.PI * 6 + (arm * Math.PI * 2 / 3);
        const radius = (i / 120) * Math.min(W, H) * 0.38;
        dots.push({
          baseX: W / 2 + Math.cos(angle) * radius,
          baseY: H / 2 + Math.sin(angle) * radius,
          x: 0, y: 0,
          r: Math.random() * 1.5 + 0.3,
          a: Math.random() * 0.8 + 0.2,
          speed: (Math.random() * 0.0003 + 0.0001) * (arm % 2 === 0 ? 1 : -1),
          angle: angle,
          radius: radius,
          arm,
        });
      }
    }

    let t = 0;
    function draw() {
      ctx.clearRect(0, 0, W, H);
      t += 0.003;
      dots.forEach(d => {
        d.angle += d.speed;
        d.x = W / 2 + Math.cos(d.angle) * d.radius;
        d.y = H / 2 + Math.sin(d.angle) * d.radius;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        const colors = ['rgba(147,51,234,', 'rgba(244,63,94,', 'rgba(245,158,11,'];
        ctx.fillStyle = colors[d.arm % 3] + d.a + ')';
        ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw();
  }

  /* ── Init ── */
  function init() {
    initDoor();
    initFestivals();
    initGifts();
    initFinalGift();
    initIntroCanvas();
  }

  return { init };
})();
