// frontend/tailwind.config.js

/** @type {import('tailwindcss').Config} */
module.exports = {
  // CRITICAL: Tells Tailwind to scan all JavaScript/JSX files in the src folder
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}