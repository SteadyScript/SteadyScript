/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        stability: {
          stable: '#22c55e',
          warning: '#eab308',
          unstable: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
