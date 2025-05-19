export type TournamentSeriesBasic = {
  id: number;
  series_name: string;
  url: string | null;
  display_order: number;
  game: string;
  mode: string;
  is_historical: boolean;
  is_public: boolean;
  short_description: string;
  logo: string | null;
  organizer: string;
  location: string;
  discord_invite: string | null;
};

export type TournamentSeries = TournamentSeriesBasic & {
  description: string;
  ruleset: string;
};
