/* eslint-disable @typescript-eslint/no-explicit-any */
import type { Color } from '$lib/types/colors';
import type { Tournament } from '$lib/types/tournament';
import type { PlacementOrganizer } from '$lib/types/placement-organizer';
import type { TeamRoster } from '$lib/types/team-roster';

export function check_registrations_open(tournament: Tournament) {
  if (!tournament.registrations_open) {
    return false;
  }
  const registration_deadline: Date | null = tournament.registration_deadline
    ? new Date(tournament.registration_deadline * 1000)
    : null;
  if (!registration_deadline) {
    return true;
  }
  const now = new Date().getTime();
  if (registration_deadline.getTime() < now) {
    return false;
  }
  return true;
}

export function sort_placement_list(a: PlacementOrganizer, b: PlacementOrganizer) {
  if (a.placement === b.placement) {
    return 0;
  }
  if (a.is_disqualified || a.placement === null) {
    return 1;
  }
  if (b.is_disqualified || b.placement === null) {
    return -1;
  }
  return a.placement < b.placement ? -1 : 1;
}

export function findNumberOfDaysBetweenDates(start: number, end: number, isMs: boolean = false) {
  const timeInDay = isMs ? 86400000 : 86400; // js/ts uses milliseconds while Python uses seconds
  return Math.floor((end - start) / timeInDay);
}

export function sortFilterRosters(rosters: TeamRoster[], show_pending: boolean = false, has_players: boolean = false) {
  const sort_filtered = rosters
    .filter(
      (r) =>
        (r.approval_status === 'approved' || (show_pending && r.approval_status === 'pending')) && // show approved, and pending if specified
        (!has_players || r.players.length > 0), // if has_players is false, don't check for # of players
    )
    .sort((a, b) => game_order[a.game] - game_order[b.game]); // sort rosters in game order
  return sort_filtered;
}

export const valid_games = ['mkworld', 'mk8dx', 'mk8', 'mkw', 'mkt', 'mk7', 'smk'];
export const game_abbreviations: { [key: string]: string } = {
  mkworld: 'MKWorld',
  mk8dx: 'MK8DX',
  mk8: 'MK8',
  mkw: 'MKWii',
  mkt: 'MKTour',
  mk7: 'MK7',
  smk: 'SMK',
  mk64: 'MK64',
  mkdd: 'MKDD',
  mksc: 'MKSC',
  mkds: 'MKDS',
};
export const game_order: { [key: string]: number } = {
  mkworld: 0,
  mk8dx: 1,
  mk8: 2,
  mkw: 3,
  mkt: 4,
  mk7: 5,
  smk: 6,
};
export const fc_types = ['switch', 'nnid', 'mkw', 'mkt', '3ds'];
export const game_fc_types: { [key: string]: string } = {
  mkworld: 'switch',
  mk8dx: 'switch',
  mk8: 'nnid',
  mkw: 'mkw',
  mkt: 'mkt',
  mk7: '3ds',
  smk: 'switch',
};
export const fc_type_order: { [key: string]: number } = {
  switch: 0,
  nnid: 1,
  mkw: 2,
  mkt: 3,
  '3ds': 4,
};
export const valid_modes: { [key: string]: string[] } = {
  mkworld: ['150cc', '200cc'],
  mk8dx: [
    '150cc',
    '200cc',
    'mixed_battle',
    'balloon_battle',
    'shine_thief',
    'bobomb_blast',
    'coin_runners',
    'renegade_roundup',
    'match_race',
    'mixed',
  ],
  mk8: ['150cc', '200cc'],
  mkw: ['rt', 'ct'],
  mkt: ['vsrace'],
  mk7: ['vsrace'],
  smk: ['match_race'],
};
export const valid_team_games = ['mkworld', 'mk8dx', 'mkw', 'mkt'];
export const valid_team_modes: { [key: string]: string[] } = {
  mkworld: ['150cc', '200cc'],
  mk8dx: ['150cc', '200cc'],
  mkw: ['rt', 'ct'],
  mkt: ['vsrace'],
};
export const colors: Color[] = [
  {
    id: 0,
    label: 'RED_1',
    value: '#ef5350',
  },
  {
    id: 1,
    label: 'ORANGE_1',
    value: '#ffa726',
  },
  {
    id: 2,
    label: 'YELLOW_1',
    value: '#d4e157',
  },
  {
    id: 3,
    label: 'GREEN_1',
    value: '#66bb6a',
  },
  {
    id: 4,
    label: 'AQUA_1',
    value: '#26a69a',
  },
  {
    id: 5,
    label: 'BLUE_1',
    value: '#29b6f6',
  },
  {
    id: 6,
    label: 'INDIGO_1',
    value: '#5c6bc0',
  },
  {
    id: 7,
    label: 'PURPLE_1',
    value: '#7e57c2',
  },
  {
    id: 8,
    label: 'PINK_1',
    value: '#ec407a',
  },
  {
    id: 9,
    label: 'GREY_1',
    value: '#888888;',
  },
  {
    id: 10,
    label: 'RED_2',
    value: '#c62828',
  },
  {
    id: 11,
    label: 'ORANGE_2',
    value: '#ef6c00',
  },
  {
    id: 12,
    label: 'YELLOW_2',
    value: '#9e9d24',
  },
  {
    id: 13,
    label: 'GREEN_2',
    value: '#2e7d32;',
  },
  {
    id: 14,
    label: 'AQUA_2',
    value: '#00897b',
  },
  {
    id: 15,
    label: 'BLUE_2',
    value: '#0277bd;',
  },
  {
    id: 16,
    label: 'INDIGO_2',
    value: '#283593',
  },
  {
    id: 17,
    label: 'PURPLE_2',
    value: '#4527a0',
  },
  {
    id: 18,
    label: 'PINK_2',
    value: '#ad1457',
  },
  {
    id: 19,
    label: 'GREY_2',
    value: '#444444',
  },
  {
    id: 20,
    label: 'RED_3',
    value: '#d44a48',
  },
  {
    id: 21,
    label: 'ORANGE_3',
    value: '#e69422',
  },
  {
    id: 22,
    label: 'YELLOW_3',
    value: '#bdc74e',
  },
  {
    id: 23,
    label: 'GREEN_3',
    value: '#4a874c',
  },
  {
    id: 24,
    label: 'AQUA_3',
    value: '#208c81',
  },
  {
    id: 25,
    label: 'BLUE_3',
    value: '#25a5db',
  },
  {
    id: 26,
    label: 'INDIGO_3',
    value: '#505ca6',
  },
  {
    id: 27,
    label: 'PURPLE_3',
    value: '#6c4ca8',
  },
  {
    id: 28,
    label: 'PINK_3',
    value: '#d13b6f',
  },
  {
    id: 29,
    label: 'GREY_3',
    value: '#545454',
  },
  {
    id: 30,
    label: 'RED_4',
    value: '#ab2424',
  },
  {
    id: 31,
    label: 'ORANGE_4',
    value: '#d45f00',
  },
  {
    id: 32,
    label: 'YELLOW_4',
    value: '#82801e',
  },
  {
    id: 33,
    label: 'GREEN_4',
    value: '#205723',
  },
  {
    id: 34,
    label: 'AQUA_4',
    value: '#006e61',
  },
  {
    id: 35,
    label: 'BLUE_4',
    value: '#0369a3',
  },
  {
    id: 36,
    label: 'INDIGO_4',
    value: '#222d78',
  },
  {
    id: 37,
    label: 'PURPLE_4',
    value: '#382185',
  },
  {
    id: 38,
    label: 'PINK_4',
    value: '#91114b',
  },
  {
    id: 39,
    label: 'BLACK',
    value: '#000000',
  },
];
export const default_player_ban_options: string[] = [
  'Alternate Account',
  'Alting',
  'Harassment',
  'Sexual Misconduct',
  'Other',
];
