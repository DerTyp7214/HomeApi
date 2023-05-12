import flowbite from 'flowbite/plugin'

/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        primary: { 50: '#ebf5ff', 100: '#fff1ee', 200: '#ffe4de', 300: '#ffd5cc', 400: '#ffbcad', 500: '#fe795d', 600: '#ef562f', 700: '#eb4f27', 800: '#d3330a', 900: '#d3330a' }
      }
    },
  },
  plugins: [
    flowbite,
  ],
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{svelte,js,ts}',
    './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}',
  ],
}

