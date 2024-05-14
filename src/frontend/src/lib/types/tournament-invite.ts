export type TournamentInvite = {
  invite_id: number;
  tournament_id: number;
  timestamp: number;
  squad_name: string | null;
  squad_tag: string | null;
  squad_color: number | null;
  tournament_name: string;
  tournament_game: string;
  tournament_mode: string;
};
