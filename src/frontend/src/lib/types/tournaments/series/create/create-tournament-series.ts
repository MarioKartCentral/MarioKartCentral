export type CreateTournamentSeries = {
  series_name: string;
  url: string | null;
  display_order: number;
  game: string;
  mode: string;
  is_historical: boolean;
  is_public: boolean;
  description: string;
  logo: string | null;
  ruleset: string;
  organizer: string;
  location: string | null;
};
