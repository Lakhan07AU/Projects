# 🎂 A Journey Through Your Life — Birthday Website

A premium, cinematic, multi-section birthday website for your sister.  
Dark luxury aesthetic · Glassmorphism · Parallax · Particles · Crossfading audio · Lightbox gallery

---

## 📁 Project Structure

```
birthday-website/
├── index.html              ← Main file (open this in browser)
├── data/
│   └── content.js          ← ✏️  ALL YOUR CONTENT GOES HERE
├── css/
│   ├── style.css           ← Design tokens, base styles, components
│   └── themes.css          ← Per-section visual themes
├── js/
│   ├── app.js              ← Bootstrap & preloader
│   ├── cursor.js           ← Custom heart cursor
│   ├── audio.js            ← Section crossfade audio manager
│   ├── particles.js        ← Stars, fireflies, rain, confetti, fireworks
│   ├── effects.js          ← GSAP scroll animations, reveal effects
│   ├── gallery.js          ← Lightbox, photo grid, video theater
│   └── interactions.js     ← Door, festival modals, gifts, final surprise
└── assets/
    ├── images/
    │   ├── childhood/      ← Baby photos, school photos
    │   ├── family/         ← Family photos
    │   ├── festivals/      ← Diwali, Holi, Raksha Bandhan photos
    │   ├── school/         ← School life photos
    │   ├── college/        ← College photos
    │   ├── memories/       ← General memory photos
    │   └── final/          ← Final gift reveal photos
    ├── videos/             ← MP4 videos for the Memory Theater
    └── audio/              ← MP3 tracks (one per section)
```

---

## ✏️ How To Personalize (Step by Step)

### Step 1 — Open `data/content.js`

This is your **single control panel**. Everything personal is here.

```js
sister: {
  name:    "Priya",       // ← Her real name
  nickname: "Didi",
  birthday: "2000-03-15", // ← Her birthday
  age:      24,
}
```

### Step 2 — Add Photos

Place photos in the correct folder under `assets/images/`.  
Then in `index.html`, find each `photo-placeholder` div and replace it with:

```html
<!-- BEFORE (placeholder): -->
<div class="photo-placeholder">...</div>

<!-- AFTER (real photo): -->
<img src="assets/images/childhood/baby1.jpg" alt="Baby photo" loading="lazy" />
```

Or set `data-src` on the wrapping element for the lightbox:

```html
<div class="photo-item" data-lightbox data-src="assets/images/childhood/school.jpg" data-caption="First day of school 🎒">
  <img src="assets/images/childhood/school.jpg" alt="School" loading="lazy" />
</div>
```

### Step 3 — Add Audio

Drop MP3 files into `assets/audio/` and update paths in `data/content.js`:

```js
audio: {
  intro:     "assets/audio/intro.mp3",
  childhood: "assets/audio/childhood.mp3",
  family:    "assets/audio/family.mp3",
  // ... one per section
}
```

**Suggested free music sources:**
- [Pixabay Music](https://pixabay.com/music/) — Royalty free
- [Free Music Archive](https://freemusicarchive.org/)
- [Bensound](https://www.bensound.com/)

### Step 4 — Add Videos (Memory Theater)

Drop MP4 files into `assets/videos/` and update in `data/content.js`:

```js
videos: [
  { src: "assets/videos/childhood.mp4", label: "Childhood Memories 🧸" },
  { src: "assets/videos/birthday.mp4",  label: "Birthday Wishes 🎂" },
]
```

### Step 5 — Add Festival Photos

In `data/content.js`, add photo paths inside each festival:

```js
festivals: {
  diwali: {
    photos: [
      { src: "assets/images/festivals/diwali1.jpg", caption: "Diwali 2022 🪔" },
      { src: "assets/images/festivals/diwali2.jpg", caption: "Lighting diyas together" },
    ]
  }
}
```

### Step 6 — Personalize Gift Messages

In `data/content.js`, edit the `gifts` array:

```js
gifts: [
  {
    icon:    "📜",
    title:   "A Letter From My Heart",
    message: "Your personal heartfelt letter here...\n\nWrite whatever you've never said out loud.",
  },
  // ... 5 more gifts
]
```

### Step 7 — Add Voice Messages (Wishes Page)

Record voice notes from family members and add paths:

```html
<!-- In index.html, find wish-play-btn and add data-audio-src -->
<button class="wish-play-btn" data-audio-src="assets/audio/papa-wish.mp3">
  🎵 Play Voice Note
</button>
```

### Step 8 — Customize the Letter (Final Page)

Find the `letter-body` div in `index.html` and write your personal letter.  
Replace the placeholder text with your real words.

### Step 9 — Update Achievement Cards (Success Page)

Find `.achievement-card` in `index.html` and replace:

```html
<h3 class="achievement-title">Education</h3>
<p class="achievement-desc">B.Tech Computer Science, 2022 🎓</p>
```

---

## 🚀 How To Open

**Option A — Direct browser**
Just double-click `index.html`. Works for most features.

**Option B — Local server (recommended for audio/video)**
```bash
# Python
python -m http.server 8080

# Node.js
npx serve .

# VS Code
Install "Live Server" extension → Right click index.html → Open with Live Server
```

Then open `http://localhost:8080` in your browser.

---

## 🎨 Customizing Colors

All colors are CSS variables in `css/style.css` at the top:

```css
:root {
  --c-rose:        #f43f5e;   /* Primary accent */
  --c-gold:        #f59e0b;   /* Gold highlights */
  --c-purple-glow: #9333ea;   /* Purple glow */
  --c-champagne:   #fde68a;   /* Warm text */
}
```

---

## 📱 Mobile Support

The website is fully responsive. On mobile:
- Custom cursor is hidden (uses default)
- Photo grids adapt to 2 columns
- Navigation dots are hidden (use scroll instead)
- All touch gestures work in the lightbox (swipe left/right)

---

## 🎁 Sections at a Glance

| # | Section | Special Feature |
|---|---------|-----------------|
| 0 | **Portal** | Galaxy canvas + magic door |
| 1 | **Childhood** | Rope-hung polaroid photos + butterflies |
| 2 | **Family** | Fairy lights + floating hearts + photo wall |
| 3 | **Festivals** | 4 clickable cards → modal with photos |
| 4 | **School** | Notebook bg + timeline + paper planes |
| 5 | **College** | Night city + floating items |
| 6 | **Hard Times** | Rain + window frame + thunder |
| 7 | **Loneliness** | Moon + falling leaves + word reveal |
| 8 | **Success** | Sunrise + mountains + achievement cards |
| 9 | **Theater** | Cinema curtains + video player |
| 10 | **Gifts** | 6 clickable 3D gift boxes → reveals |
| 11 | **Wishes** | Family wish cards + voice note player |
| 12 | **Finale** | Letter + 3D gift explosion + fireworks |

---

## ❤️ Made with love

Every pixel placed with care. Every line of code written with emotion.  
Because she deserves the most beautiful birthday surprise.

**Happy Birthday to your sister! 🎂**
