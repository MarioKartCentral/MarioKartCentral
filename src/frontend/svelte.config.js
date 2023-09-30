import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

function getEntriesForLocale(locale) {
  return [
    `/${locale}`,
    `/${locale}/tournaments/details`,
    `/${locale}/player-signup`,
    `/${locale}/registry/players/edit-profile`,
    `/${locale}/registry/players/profile`,
    `/${locale}/registry/invites`,
    `/${locale}/registry/teams/profile`,
    `/${locale}/registry/teams/create`,
    `/${locale}/registry/teams/edit`,
    `/${locale}/registry/teams/manage_rosters`,
    `/${locale}/moderator/approve_teams`,
    `/${locale}/moderator/approve_team_edits`,
    `/${locale}/moderator/approve_transfers`,
  ];
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
