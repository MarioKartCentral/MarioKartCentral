import type { TournamentPlayer } from './tournament-player';
import type { TournamentSquad } from './tournament-squad';

export type TournamentPlacementSimple = {
  registration_id: number;
  placement: number | null;
  placement_description: string | null;
  placement_lower_bound: number | null;
  is_disqualified: boolean;
};

export type TournamentPlacement = TournamentPlacementSimple & {
  player: TournamentPlayer | null;
  squad: TournamentSquad | null;
};

export type TournamentPlacementList = {
  tournament_id: number;
  is_squad: boolean;
  placements: TournamentPlacement[];
  unplaced: TournamentPlacement[];
};
