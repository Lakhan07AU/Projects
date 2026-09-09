/**
 * audio.js — Section-based crossfading audio manager
 */
window.AudioManager = (function () {
  'use strict';

  const content = window.BIRTHDAY_CONTENT || {};
  const tracks  = content.audio || {};

  let currentTrack  = null;
  let currentAudio  = null;
  let isMuted       = false;
  let volume        = 0.35;
  let fadeInterval  = null;
  let userInteracted = false;

  const muteBtn    = document.getElementById('muteBtn');
  const muteIcon   = document.getElementById('muteIcon');
  const vizWrapper = document.getElementById('audioVisualizer');

  /* ── Public API ── */
  function play(trackKey) {
    if (!userInteracted) return;
    if (trackKey === currentTrack) return;

    const src = tracks[trackKey];
    if (!src) return; // No file configured

    currentTrack = trackKey;
    fadeOut(currentAudio, () => {
      currentAudio = createAudio(src);
      fadeIn(currentAudio);
    });
  }

  function toggle() {
    isMuted = !isMuted;
    if (currentAudio) currentAudio.muted = isMuted;
    updateMuteUI();
  }

  function enableAudio() {
    userInteracted = true;
  }

  /* ── Internals ── */
  function createAudio(src) {
    const a = new Audio(src);
    a.loop   = true;
    a.volume = 0;
    a.muted  = isMuted;
    a.play().catch(() => {}); // Autoplay may be blocked
    return a;
  }

  function fadeIn(audio) {
    if (!audio) return;
    clearInterval(fadeInterval);
    let v = 0;
    fadeInterval = setInterval(() => {
      v = Math.min(v + 0.02, volume);
      audio.volume = v;
      if (v >= volume) clearInterval(fadeInterval);
    }, 80);
  }

  function fadeOut(audio, callback) {
    if (!audio) { callback && callback(); return; }
    clearInterval(fadeInterval);
    let v = audio.volume;
    fadeInterval = setInterval(() => {
      v = Math.max(v - 0.03, 0);
      audio.volume = v;
      if (v <= 0) {
        clearInterval(fadeInterval);
        audio.pause();
        callback && callback();
      }
    }, 60);
  }

  function updateMuteUI() {
    if (!muteIcon) return;
    muteIcon.className = isMuted
      ? 'fa-solid fa-volume-xmark'
      : 'fa-solid fa-volume-high';
    if (vizWrapper) vizWrapper.classList.toggle('audio-paused', isMuted);
  }

  /* ── Button listeners ── */
  if (muteBtn) {
    muteBtn.addEventListener('click', () => {
      enableAudio();
      toggle();
    });
  }

  const prevBtn = document.getElementById('prevTrackBtn');
  const nextBtn = document.getElementById('nextTrackBtn');
  const keys    = Object.keys(tracks);

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      enableAudio();
      const idx = keys.indexOf(currentTrack);
      const prev = keys[(idx - 1 + keys.length) % keys.length];
      currentTrack = null; // force reload
      play(prev);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      enableAudio();
      const idx = keys.indexOf(currentTrack);
      const next = keys[(idx + 1) % keys.length];
      currentTrack = null;
      play(next);
    });
  }

  /* ── Voice note buttons ── */
  document.querySelectorAll('.wish-play-btn').forEach(btn => {
    let noteAudio = null;
    let playing   = false;
    btn.addEventListener('click', () => {
      enableAudio();
      const src = btn.dataset.audioSrc;
      if (!src) {
        btn.textContent = '🎵 (Add voice recording)';
        return;
      }
      if (playing && noteAudio) {
        noteAudio.pause();
        noteAudio.currentTime = 0;
        btn.innerHTML = '🎵 Play Voice Note';
        playing = false;
      } else {
        noteAudio = new Audio(src);
        noteAudio.play().catch(() => {});
        noteAudio.onended = () => {
          btn.innerHTML = '🎵 Play Voice Note';
          playing = false;
        };
        btn.innerHTML = '⏸ Playing...';
        playing = true;
      }
    });
  });

  return { play, toggle, enableAudio };
})();
