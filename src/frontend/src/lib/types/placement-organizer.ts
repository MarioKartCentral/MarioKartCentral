import type { TournamentPlayer } from '$lib/types/tournament-player';
import type { TournamentSquad } from './tournament-squad';

export type PlacementOrganizer = {
  id: number;
  placement: number | null;
  description: string | null;
  tie: boolean;
  player: TournamentPlayer | null;
  squad: TournamentSquad | null;
};
