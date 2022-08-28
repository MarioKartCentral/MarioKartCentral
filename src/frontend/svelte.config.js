import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://github.com/sveltejs/svelte-preprocess
  // for more information about preprocessors
  preprocess: preprocess({
    typescript: true
  }),

  kit: {
    adapter: adapter(),

    alias: {
      $i18n: 'src/i18n'
    },

    browser: {
      router: false
      // hydrate: false
    },

    prerender: {
      default: true,
      entries: locales.map((l) => `/${l}`)
    },
    
    trailingSlash: 'never'
  }
};

export default config;
