export type CreateTournamentSeries = {
  series_id: number | null;
  series_name: string;
  url: string | null;
  display_order: number;
  game: string;
  mode: string;
  is_historical: boolean;
  is_public: boolean;
  short_description: string;
  description: string;
  logo: string | null;
  logo_file: string | null;
  remove_logo: boolean;
  ruleset: string;
  organizer: string;
  location: string | null;
};
