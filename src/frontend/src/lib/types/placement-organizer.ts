import type { TournamentSquad } from './tournament-squad';

export type PlacementOrganizer = {
  id: number;
  placement: number | null;
  description: string | null;
  tie: boolean;
  bounded: boolean;
  placement_lower_bound: number | null;
  is_disqualified: boolean;
  squad: TournamentSquad;
};
