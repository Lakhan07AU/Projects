/**
 * ============================================================
 *  BIRTHDAY WEBSITE — CONTENT CONFIGURATION
 *  ============================================================
 *  Edit this file to personalize the website for your sister.
 *  All photos, videos, audio, names, and messages are here.
 *  ============================================================
 */

window.BIRTHDAY_CONTENT = {

  /* ----------------------------------------------------------
   * BASIC INFO
   * ---------------------------------------------------------- */
  sister: {
    name:        "Your Sister's Name",   // ← Change this
    nickname:    "Didi",                  // ← Her nickname
    birthday:    "2024-01-01",            // ← Her birthday (YYYY-MM-DD)
    age:         25,                      // ← Her age
  },

  author: {
    name:        "Your Name",             // ← Your name
    relation:    "Your Brother / Sister", // ← Your relation
  },

  /* ----------------------------------------------------------
   * AUDIO TRACKS
   * Place MP3 files in assets/audio/ and fill in the paths.
   * Each key matches the data-audio attribute on sections.
   * ---------------------------------------------------------- */
  audio: {
    intro:      "assets/audio/intro.mp3",
    childhood:  "assets/audio/childhood.mp3",
    family:     "assets/audio/family.mp3",
    festival:   "assets/audio/festival.mp3",
    school:     "assets/audio/school.mp3",
    college:    "assets/audio/college.mp3",
    rain:       "assets/audio/rain.mp3",
    lonely:     "assets/audio/lonely.mp3",
    success:    "assets/audio/success.mp3",
    theater:    "assets/audio/theater.mp3",
    gifts:      "assets/audio/gifts.mp3",
    wishes:     "assets/audio/wishes.mp3",
    ending:     "assets/audio/ending.mp3",
  },

  /* ----------------------------------------------------------
   * VIDEOS — Memory Theater
   * Place video files in assets/videos/ and fill paths below.
   * ---------------------------------------------------------- */
  videos: [
    {
      src:       "",   // e.g. "assets/videos/childhood.mp4"
      thumb:     "",   // e.g. "assets/images/thumbs/childhood.jpg"
      label:     "Childhood Memories 🧸",
    },
    {
      src:       "",
      thumb:     "",
      label:     "Family Moments 👨‍👩‍👧",
    },
    {
      src:       "",
      thumb:     "",
      label:     "Festival Fun 🪔",
    },
    {
      src:       "",
      thumb:     "",
      label:     "Birthday Wishes 🎂",
    },
    {
      src:       "",
      thumb:     "",
      label:     "Add More Videos ✨",
    },
  ],

  /* ----------------------------------------------------------
   * FESTIVAL MODAL CONTENT
   * ---------------------------------------------------------- */
  festivals: {
    diwali: {
      title:    "Diwali with You 🪔",
      emoji:    "🪔",
      color:    "#ff8c00",
      memory:   "Every Diwali, you would light the first diya and our whole house would glow — not just from the diyas, but from your smile.",
      photos:   [
        // { src: "assets/images/festivals/diwali1.jpg", caption: "Diwali 2022" },
      ],
    },
    holi: {
      title:    "Holi of Colors 🎨",
      emoji:    "🎨",
      color:    "#ff6b6b",
      memory:   "You always saved the biggest water balloon for me. Every Holi with you was the most colorful day of the year.",
      photos:   [],
    },
    raksha: {
      title:    "Raksha Bandhan 🎀",
      emoji:    "🎀",
      color:    "#ffd700",
      memory:   "When you tied the rakhi on my wrist, I felt the weight of my responsibility and the warmth of your love at the same time.",
      photos:   [],
    },
    birthday: {
      title:    "Your Birthday! 🎂",
      emoji:    "🎂",
      color:    "#9333ea",
      memory:   "Every year your birthday reminds me that the best gift life ever gave me was you. Happy Birthday, didi!",
      photos:   [],
    },
  },

  /* ----------------------------------------------------------
   * SECRET GIFTS (Page 10)
   * ---------------------------------------------------------- */
  gifts: [
    {
      icon:     "📜",
      title:    "A Secret Letter",
      message:  "Write a heartfelt letter here. Tell her something you've never said out loud. This is the most personal gift of all.\n\nShare a memory only the two of you share. Make her cry happy tears.",
    },
    {
      icon:     "🌸",
      title:    "A Hidden Memory",
      message:  "Remember that one evening when we sat on the rooftop and watched the sunset? You said 'moments like these are what life is made of.' I think of that every time I miss you.",
    },
    {
      icon:     "😂",
      title:    "The Funniest Secret",
      message:  "Add a funny shared memory or inside joke here! Something that will make her laugh so hard she snorts. 😂\n\n(Replace this with your real funny memory!)",
    },
    {
      icon:     "🤝",
      title:    "My Promise To You",
      message:  "I promise to always be there — in every celebration and every storm.\nI promise to never let you feel alone.\nI promise to make you proud.\nI promise to always love you, unconditionally, forever.",
    },
    {
      icon:     "🎵",
      title:    "Our Song",
      message:  "Add the name of the song that always reminds you of each other. Or a song she loves. Or your family's favourite song.\n\n♪ [Song Name Here] — [Artist] ♪\n\n\"This song will always be ours.\"",
    },
    {
      icon:     "💝",
      title:    "The Final Surprise",
      message:  "This is where you put the biggest surprise — maybe a trip plan, maybe a future date for just the two of you, maybe something you ordered for her.\n\nMake it personal. Make it unforgettable. 💝",
    },
  ],

  /* ----------------------------------------------------------
   * WISHES (Page 11) — Override the HTML defaults or leave as-is
   * ---------------------------------------------------------- */
  wishes: [
    // {
    //   name:     "Papa",
    //   relation: "Father",
    //   avatar:   "👨",
    //   photo:    "",   // path to photo
    //   message:  "Your wish message here...",
    //   audioSrc: "",   // path to voice recording
    // },
  ],

  /* ----------------------------------------------------------
   * FALLING LEAVES — Loneliness section
   * ---------------------------------------------------------- */
  leaves: ["🍂", "🍁", "🌿", "🍃", "🍂", "🍁"],

  /* ----------------------------------------------------------
   * FIREFLY COUNT
   * ---------------------------------------------------------- */
  fireflyCount: 20,
  starCount: 150,

};
