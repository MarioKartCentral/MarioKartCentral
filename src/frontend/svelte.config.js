import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

function getEntriesForLocale(locale) {
  return [`/${locale}`, `/${locale}/tournaments/details`, `/${locale}/player-signup`];
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: preprocess(),

  kit: {
    adapter: adapter(),

    alias: {
      $i18n: 'src/i18n',
    },

    prerender: {
      //entries: locales.map((l) => `/${l}`)
      entries: locales.flatMap(getEntriesForLocale),
    },
  },
};

export default config;
