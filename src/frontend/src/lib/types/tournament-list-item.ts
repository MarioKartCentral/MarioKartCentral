export type TournamentListItem = {
  id: number;
  name: string;
  game: string;
  mode: string;
  date_start: number;
  date_end: number;
  series_id: number;
  series_name: string | null;
  series_url: string | null;
  series_description: string | null;
  is_squad: boolean;
  teams_allowed: boolean;
  description: string;
  logo: string | null;
};
