import type { TournamentPlayer } from '$lib/types/tournament-player';
import type { RosterBasic } from './roster-basic';

export type TournamentSquad = {
  id: number;
  name: string | null;
  tag: string | null;
  color: number;
  timestamp: number;
  is_registered: boolean;
  is_approved: boolean;
  players: TournamentPlayer[];
  rosters: RosterBasic[];
};
