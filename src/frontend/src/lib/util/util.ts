/* eslint-disable @typescript-eslint/no-explicit-any */
import type { Color } from '$lib/types/colors';
import type { Tournament } from '$lib/types/tournament';
import type { TournamentSquad } from '$lib/types/tournament-squad';
import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
import type { PlacementOrganizer } from '$lib/types/placement-organizer';

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

export async function unregister(
  registration: MyTournamentRegistration,
  tournament: Tournament,
  squad: TournamentSquad | null = null,
) {
  if (!registration.player) {
    return;
  }
  if (registration.player.is_squad_captain && squad && squad.players.length > 1) {
    alert('Please unregister this squad or set another player as captain before unregistering for this tournament');
    return;
  }
  const conf = window.confirm('Are you sure you would like to unregister for this tournament?');
  if (!conf) {
    return;
  }
  const payload = {
    squad_id: registration.player.squad_id,
  };
  console.log(payload);
  const endpoint = `/api/tournaments/${tournament.id}/unregister`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (response.status < 300) {
    window.location.reload();
  } else {
    alert(`Failed to unregister: ${result['title']}`);
  }
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

export const valid_games: { [key: string]: string } = {
  mk8dx: 'Mario Kart 8 Deluxe',
  mk8: 'Mario Kart 8',
  mkw: 'Mario Kart Wii',
  mkt: 'Mario Kart Tour',
  mk7: 'Mario Kart 7',
  smk: 'Super Mario Kart',
};
export const valid_modes: { [key: string]: string[] } = {
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
export const mode_names: { [key: string]: string } = {
  '150cc': '150cc',
  '200cc': '200cc',
  mixed_battle: 'Battle (Mixed)',
  balloon_battle: 'Balloon Battle',
  shine_thief: 'Shine Thief',
  bobomb_blast: 'Bob-omb Blast',
  coin_runners: 'Coin Runners',
  renegade_roundup: 'Renegade Roundup',
  match_race: 'Match Race',
  mixed: 'Mixed Format',
  rt: 'Regular Tracks',
  ct: 'Custom Tracks',
  vsrace: 'VS Race',
};
export const colors: Color[] = [
  {
    label: 'RED_1',
    value: '#ef5350',
  },
  {
    label: 'ORANGE_1',
    value: '#ffa726',
  },
  {
    label: 'YELLOW_1',
    value: '#d4e157',
  },
  {
    label: 'GREEN_1',
    value: '#66bb6a',
  },
  {
    label: 'AQUA_1',
    value: '#26a69a',
  },
  {
    label: 'BLUE_1',
    value: '#29b6f6',
  },
  {
    label: 'INDIGO_1',
    value: '#5c6bc0',
  },
  {
    label: 'PURPLE_1',
    value: '#7e57c2',
  },
  {
    label: 'PINK_1',
    value: '#ec407a',
  },
  {
    label: 'GREY_1',
    value: '#888888;',
  },
  {
    label: 'RED_2',
    value: '#c62828',
  },
  {
    label: 'ORANGE_2',
    value: '#ef6c00',
  },
  {
    label: 'YELLOW_2',
    value: '#9e9d24',
  },
  {
    label: 'GREEN_2',
    value: '#2e7d32;',
  },
  {
    label: 'AQUA_2',
    value: '#00897b',
  },
  {
    label: 'BLUE_2',
    value: '#0277bd;',
  },
  {
    label: 'INDIGO_2',
    value: '#283593',
  },
  {
    label: 'PURPLE_2',
    value: '#4527a0',
  },
  {
    label: 'PINK_2',
    value: '#ad1457',
  },
  {
    label: 'GREY_2',
    value: '#444444',
  },
  {
    label: 'RED_3',
    value: '#d44a48',
  },
  {
    label: 'ORANGE_3',
    value: '#e69422',
  },
  {
    label: 'YELLOW_3',
    value: '#bdc74e',
  },
  {
    label: 'GREEN_3',
    value: '#4a874c',
  },
  {
    label: 'AQUA_3',
    value: '#208c81',
  },
  {
    label: 'BLUE_3',
    value: '#25a5db',
  },
  {
    label: 'INDIGO_3',
    value: '#505ca6',
  },
  {
    label: 'PURPLE_3',
    value: '#6c4ca8',
  },
  {
    label: 'PINK_3',
    value: '#d13b6f',
  },
  {
    label: 'GREY_3',
    value: '#545454',
  },
  {
    label: 'RED_4',
    value: '#ab2424',
  },
  {
    label: 'ORANGE_4',
    value: '#d45f00',
  },
  {
    label: 'YELLOW_4',
    value: '#82801e',
  },
  {
    label: 'GREEN_4',
    value: '#205723',
  },
  {
    label: 'AQUA_4',
    value: '#006e61',
  },
  {
    label: 'BLUE_4',
    value: '#0369a3',
  },
  {
    label: 'INDIGO_4',
    value: '#222d78',
  },
  {
    label: 'PURPLE_4',
    value: '#382185',
  },
  {
    label: 'PINK_4',
    value: '#91114b',
  },
  {
    label: 'BLACK',
    value: '#000000',
  },
];
