import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

function getEntriesForLocale(locale) {
  return [
    `/${locale}`,
    `/${locale}/admin/backup_db`,
    `/${locale}/time-trials`,
    `/${locale}/time-trials/edit`,
    `/${locale}/time-trials/submit`,
    `/${locale}/time-trials/mkworld`,
    `/${locale}/time-trials/mkworld/leaderboard`,
    `/${locale}/time-trials/mkworld/validation`,
    `/${locale}/time-trials/mkworld/timesheet`,
    `/${locale}/tournaments/details`,
    `/${locale}/tournaments/create`,
    `/${locale}/tournaments/create/select_template`,
    `/${locale}/tournaments/edit`,
    `/${locale}/tournaments/edit_placements`,
    `/${locale}/tournaments/edit_placements/raw`,
    `/${locale}/tournaments/edit_placements/raw_player_id`,
    `/${locale}/tournaments/manage_roles`,
    `/${locale}/tournaments/posts/create`,
    `/${locale}/tournaments/posts/edit`,
    `/${locale}/tournaments/posts/view`,
    `/${locale}/tournaments/series`,
    `/${locale}/tournaments/series/create`,
    `/${locale}/tournaments/series/create_template`,
    `/${locale}/tournaments/series/create_tournament`,
    `/${locale}/tournaments/series/create_tournament/select_template`,
    `/${locale}/tournaments/series/details`,
    `/${locale}/tournaments/series/edit`,
    `/${locale}/tournaments/series/manage_roles`,
    `/${locale}/tournaments/series/posts/create`,
    `/${locale}/tournaments/series/posts/edit`,
    `/${locale}/tournaments/series/posts/view`,
    `/${locale}/tournaments/series/templates`,
    `/${locale}/tournaments/templates`,
    `/${locale}/tournaments/templates/create`,
    `/${locale}/tournaments/templates/edit`,
    `/${locale}/posts`,
    `/${locale}/posts/create`,
    `/${locale}/posts/edit`,
    `/${locale}/posts/view`,
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
    `/${locale}/moderator/alt_detection`,
    `/${locale}/moderator/approve_player_names`,
    `/${locale}/moderator/approve_teams`,
    `/${locale}/moderator/approve_team_edits`,
    `/${locale}/moderator/approve_transfers`,
    `/${locale}/moderator/fingerprints`,
    `/${locale}/moderator/friend_code_edits`,
    `/${locale}/moderator/ip_history`,
    `/${locale}/moderator/ip_search`,
    `/${locale}/moderator/manage_user_roles`,
    `/${locale}/moderator/merge_players`,
    `/${locale}/moderator/merge_teams`,
    `/${locale}/moderator/player_bans`,
    `/${locale}/moderator/player_claims`,
    `/${locale}/moderator/shadow_players`,
    `/${locale}/moderator/users`,
    `/${locale}/moderator/users/edit`,
    `/${locale}/moderator/word_filter`,
    `/${locale}/user/api-tokens`,
    `/${locale}/user/confirm-email`,
    `/${locale}/user/login`,
    `/${locale}/user/notifications`,
    `/${locale}/user/player-signup`,
    `/${locale}/user/privacy-policy`,
    `/${locale}/user/reset-password`,
    `/${locale}/user/terms`,
    `/${locale}/user/transfer-account`,
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
