/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'plant-green': '#4ade80',
        'leaf-green': '#22c55e',
        'soil-brown': '#a16207',
        'sun-yellow': '#fbbf24',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
