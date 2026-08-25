/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,tsx}",
    "./components/**/*.{js,ts,tsx}",
    "./lib/**/*.{js,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7f6",
          100: "#d7ecea",
          200: "#b0d9d5",
          300: "#82c1bc",
          400: "#55a6a0",
          500: "#378c87",
          600: "#2a706d",
          700: "#245a58",
          800: "#204948",
          900: "#1d3d3c",
          950: "#0d2726",
        },
      },
    },
  },
  plugins: [],
};
