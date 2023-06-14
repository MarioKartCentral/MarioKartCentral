export type Tournament = {
    id: number;
    tournament_name: string;
    game: string;
    mode: string;
    start_date: Date;
    end_date: Date;
    is_squad: boolean;
    registrations_open: boolean;
    description: string;
    logo: string | null;
    url: string | null;
    registration_deadline: Date;
    min_squad_size: number;
    max_squad_size: number;
    ruleset: string;
    organizer: string | null;
    location: string | null;
    series_id: number | null;
    series_name: string | null;
    series_url: string | null;
    series_description: string | null;
}