import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

const locales = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];

// Import track constants for prerender entries
const MK8DX_TRACK_ABBREVIATIONS = {
  'Mario Kart Stadium': 'MKS',
  'Water Park': 'WP',
  'Sweet Sweet Canyon': 'SSC',
  'Thwomp Ruins': 'TR',
  'Mario Circuit': 'MC',
  'Toad Harbor': 'TH',
  'Twisted Mansion': 'TM',
  'Shy Guy Falls': 'SGF',
  'Sunshine Airport': 'SA',
  'Dolphin Shoals': 'DS',
  'Electrodrome': 'Ed',
  'Mount Wario': 'MW',
  'Cloudtop Cruise': 'CC',
  'Bone-Dry Dunes': 'BDD',
  'Bowser\'s Castle': 'BC',
  'Rainbow Road': 'RR',
  'Moo Moo Meadows': 'rMMM',
  'Mario Circuit (GBA)': 'rMC',
  'Cheep Cheep Beach': 'rCCB',
  'Toad\'s Turnpike': 'rTT',
  'Dry Dry Desert': 'rDDD',
  'Donut Plains 3': 'rDP3',
  'Royal Raceway': 'rRRy',
  'DK Jungle': 'rDKJ',
  'Wario Stadium': 'rWS',
  'Sherbet Land': 'rSL',
  'Music Park': 'rMP',
  'Yoshi Valley': 'rYV',
  'Tick-Tock Clock': 'rTTC',
  'Piranha Plant Slide': 'rPPS',
  'Grumble Volcano': 'rGV',
  'Rainbow Road (N64)': 'rRRd',
  'Yoshi Circuit': 'dYC',
  'Excitebike Arena': 'dEA',
  'Dragon Driftway': 'dDD',
  'Mute City': 'dMC',
  'Wario\'s Gold Mine': 'dWGM',
  'Rainbow Road (SNES)': 'dRR',
  'Ice Ice Outpost': 'dIIO',
  'Hyrule Circuit': 'dHC',
  'Baby Park': 'dBP',
  'Cheese Land': 'dCL',
  'Wild Woods': 'dWW',
  'Animal Crossing': 'dAC',
  'Neo Bowser City': 'dNBC',
  'Ribbon Road': 'dRiR',
  'Super Bell Subway': 'dSBS',
  'Big Blue': 'dBB',
  'Paris Promenade': 'bPP',
  'Toad Circuit': 'bTC',
  'Choco Mountain': 'bCMo',
  'Coconut Mall': 'bCMa',
  'Tokyo Blur': 'bTB',
  'Shroom Ridge': 'bSR',
  'Sky Garden': 'bSG',
  'Ninja Hideaway': 'bNH',
  'New York Minute': 'bNYM',
  'Mario Circuit 3': 'bMC3',
  'Kalimari Desert': 'bKD',
  'Waluigi Pinball': 'bWP',
  'Sydney Sprint': 'bSS',
  'Snow Land': 'bSL',
  'Mushroom Gorge': 'bMG',
  'Sky-High Sundae': 'bSHS',
  'London Loop': 'bLL',
  'Boo Lake': 'bBL',
  'Rock Rock Mountain': 'bRRM',
  'Maple Treeway': 'bMT',
  'Berlin Byways': 'bBB',
  'Peach Gardens': 'bPG',
  'Merry Mountain': 'bMM',
  'Rainbow Road (3DS)': 'bRR7',
  'Amsterdam Drift': 'bAD',
  'Riverside Park': 'bRP',
  'DK Summit': 'bDKS',
  'Yoshi\'s Island': 'bYI',
  'Bangkok Rush': 'bBR',
  'Mario Circuit (DS)': 'bMC',
  'Waluigi Stadium': 'bWS',
  'Singapore Speedway': 'bSSy',
  'Athens Dash': 'bADa',
  'Daisy Cruiser': 'bDC',
  'Moonview Highway': 'bMH',
  'Squeaky Clean Sprint': 'bSQS',
  'Los Angeles Laps': 'bLAL',
  'Sunset Wilds': 'bSW',
  'Koopa Cape': 'bKC',
  'Vancouver Velocity': 'bVV',
  'Rome Avanti': 'bRA',
  'DK Mountain': 'bDKM',
  'Daisy Circuit': 'bDCt',
  'Piranha Plant Cove': 'bPPC',
  'Madrid Drive': 'bMD',
  'Rosalina\'s Ice World': 'bRIW',
  'Bowser\'s Castle 3': 'bBC3',
  'Rainbow Road (Wii)': 'bRRW'
};

const MKWORLD_TRACK_ABBREVIATIONS = {
  'Mario Bros. Circuit': 'MBC',
  'Crown City': 'CC1', 
  'Whistlestop Summit': 'WS',
  'DK Spaceport': 'DKS',
  'Desert Hills': 'rDH',
  'Shy Guy Bazaar': 'rSGB',
  'Wario Stadium': 'rWS',
  'Airship Fortress': 'rAF',
  'DK Pass': 'rDKP',
  'Starview Peak': 'SP',
  'Sky High Sundae': 'rSHS',
  'Wario Shipyard': 'rWSh',
  'Koopa Troopa Beach': 'rKTB',
  'Faraway Oasis': 'FO',
  'Crown City 2': 'CC2',
  'Peach Stadium': 'PS1',
  'Peach Beach': 'rPB',
  'Salty Salty Speedway': 'SSS',
  'Dino Dino Jungle': 'rDDJ',
  'Great ? Block Ruins': 'GBR',
  'Cheep Cheep Falls': 'CCF',
  'Dandelion Depths': 'DD',
  'Boo Cinema': 'BCi',
  'Dry Bones Burnout': 'DBB',
  'Moo Moo Meadows': 'rMMM',
  'Choco Mountain': 'rCM',
  "Toad's Factory": 'rTF',
  "Bowser's Castle": 'BC',
  'Acorn Heights': 'AH',
  'Mario Circuit': 'MC',
  'Peach Stadium 2': 'PS2',
  'Rainbow Road': 'RR'
};

function getTimeTrialsEntriesForLocale(locale) {
  const entries = [];
  
  // Add main time trials page
  entries.push(`/${locale}/time-trials`);
  
  // Add submit page
  entries.push(`/${locale}/time-trials/submit`);
  
  // Add game selection pages
  entries.push(`/${locale}/time-trials/mk8dx`);
  entries.push(`/${locale}/time-trials/mkworld`);
  
  // Add all track pages for MK8DX using abbreviations
  Object.values(MK8DX_TRACK_ABBREVIATIONS).forEach(abbreviation => {
    entries.push(`/${locale}/time-trials/mk8dx/${abbreviation}`);
  });
  
  // Add all track pages for MKWorld using abbreviations
  Object.values(MKWORLD_TRACK_ABBREVIATIONS).forEach(abbreviation => {
    entries.push(`/${locale}/time-trials/mkworld/${abbreviation}`);
  });
  
  return entries;
}

function getEntriesForLocale(locale) {
  return [
    `/${locale}`,
    `/${locale}/admin/backup_db`,
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
    ...getTimeTrialsEntriesForLocale(locale),
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
