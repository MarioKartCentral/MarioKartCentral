/** @type {import('tailwindcss').Config}*/
const config = {
  content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'],

  plugins: [require('flowbite/plugin')],

  darkMode: 'class',

  theme: {
    extend: {
      colors: {
        // flowbite-svelte
        // primary: {
        //   50: '#FFF5F2',
        //   100: '#FFF1EE',
        //   200: '#FFE4DE',
        //   300: '#FFD5CC',
        //   400: '#FFBCAD',
        //   500: '#FE795D',
        //   600: '#EF562F',
        //   700: '#EB4F27',
        //   800: '#CC4522',
        //   900: '#A5371B'
        // }
        // green
        primary: {"50":"#f0fdf4","100":"#dcfce7","200":"#bbf7d0","300":"#86efac","400":"#4ade80","500":"#22c55e","600":"#16a34a","700":"#15803d","800":"#166534","900":"#14532d"}
      }
    }
  }
};

module.exports = config;
