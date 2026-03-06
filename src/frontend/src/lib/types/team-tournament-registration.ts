import type { RosterPlayer } from './roster-player';

export type TeamTournamentPlayer = {
  player_id: number;
  is_captain: boolean;
  is_representative: boolean;
  is_bagger_clause: boolean;
};

export type RegisterTeamRequestData = {
  squad_color: number;
  squad_name: string;
  squad_tag: string;
  roster_ids: number[];
  players: TeamTournamentPlayer[];
};

export type TeamTournamentPlayerDetailed = TeamTournamentPlayer & RosterPlayer;
