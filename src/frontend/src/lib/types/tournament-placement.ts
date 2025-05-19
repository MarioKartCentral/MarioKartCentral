import type { TournamentPlayerDetailsShort } from './tournament-player';
import type { TournamentSquad } from './tournament-squad';
import type { RosterBasic } from './roster-basic';

export type TournamentPlacementSimple = {
  registration_id: number;
  placement: number | null;
  placement_description: string | null;
  placement_lower_bound: number | null;
  is_disqualified: boolean;
};

export type TournamentPlacementSimplePlayerIDs = {
  player_ids: number[];
  placement: number | null;
  placement_description: string | null;
  placement_lower_bound: number | null;
  is_disqualified: boolean;
};

export type TournamentPlacement = TournamentPlacementSimple & {
  squad: TournamentSquad;
};

export type TournamentPlacementList = {
  tournament_id: number;
  placements: TournamentPlacement[];
  unplaced: TournamentPlacement[];
};

export type PlayerTournamentPlacement = {
  tournament_id: number;
  tournament_name: string;
  game: string;
  mode: string;
  registration_id: number | null;
  squad_name: string | null;
  team_id: number | null;
  date_start: number;
  date_end: number;
  placement: number | null;
  placement_description: string | null;
  is_disqualified: boolean;
  partners: TournamentPlayerDetailsShort[] | null;
  rosters: RosterBasic[];
};

export type PlayerTournamentResults = {
  tournament_solo_and_squad_placements: PlayerTournamentPlacement[];
  tournament_team_placements: PlayerTournamentPlacement[];
};

export type TeamTournamentPlacement = {
  tournament_id: number;
  tournament_name: string;
  game: string;
  mode: string;
  registration_id: number;
  squad_name: string | null;
  date_start: number;
  date_end: number;
  placement: number | null;
  placement_description: string | null;
  is_disqualified: boolean;
  rosters: RosterBasic[];
};

export type TeamTournamentResults = {
  tournament_team_placements: TeamTournamentPlacement[];
};
