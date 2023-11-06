export type TournamentSeries = {
    id: number;
    series_name: string;
    url: string | null;
    game: string;
    mode: string;
    is_historical: boolean;
    is_public: boolean;
    description: string;
    logo: string | null;
    ruleset: string;
    organizer: string;
    location: string;
}