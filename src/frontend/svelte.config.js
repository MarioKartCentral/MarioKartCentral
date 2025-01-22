import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

function getEntriesForLocale(locale) {
  return [
    `/${locale}`,
    `/${locale}/tournaments/details`,
    `/${locale}/tournaments/create`,
    `/${locale}/tournaments/create/select_template`,
    `/${locale}/tournaments/edit`,
    `/${locale}/tournaments/edit_placements`,
    `/${locale}/tournaments/edit_placements/raw`,
    `/${locale}/tournaments/manage_roles`,
    `/${locale}/tournaments/series`,
    `/${locale}/tournaments/series/create`,
    `/${locale}/tournaments/series/create_template`,
    `/${locale}/tournaments/series/create_tournament`,
    `/${locale}/tournaments/series/create_tournament/select_template`,
    `/${locale}/tournaments/series/details`,
    `/${locale}/tournaments/series/edit`,
    `/${locale}/tournaments/series/manage_roles`,
    `/${locale}/tournaments/series/templates`,
    `/${locale}/tournaments/templates`,
    `/${locale}/tournaments/templates/create`,
    `/${locale}/tournaments/templates/edit`,
    `/${locale}/player-signup`,
    `/${locale}/registry/players`,
    `/${locale}/registry/players/edit-profile`,
    `/${locale}/registry/players/mod-edit-profile`,
    `/${locale}/registry/players/profile`,
    `/${locale}/registry/invites`,
    `/${locale}/registry/teams`,
    `/${locale}/registry/teams/profile`,
    `/${locale}/registry/teams/create`,
    `/${locale}/registry/teams/edit`,
    `/${locale}/registry/teams/manage_roles`,
    `/${locale}/registry/teams/manage_rosters`,
    `/${locale}/registry/teams/mod/edit`,
    `/${locale}/registry/teams/mod/manage_rosters`,
    `/${locale}/registry/teams/transfers`,
    `/${locale}/moderator/approve_player_names`,
    `/${locale}/moderator/approve_teams`,
    `/${locale}/moderator/approve_team_edits`,
    `/${locale}/moderator/approve_transfers`,
    `/${locale}/moderator/manage_user_roles`,
    `/${locale}/moderator/merge_players`,
    `/${locale}/moderator/merge_teams`,
    `/${locale}/moderator/player_bans`,
    `/${locale}/moderator/player_claims`,
    `/${locale}/moderator/shadow_players`,
    `/${locale}/moderator/users`,
    `/${locale}/moderator/users/edit`,
    `/${locale}/moderator/word_filter`,
    `/${locale}/notifications`,
  ];
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: [preprocess(), vitePreprocess({})],

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
