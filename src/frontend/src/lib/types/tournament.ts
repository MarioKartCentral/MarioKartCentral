export type Tournament = {
    id: number;
    tournament_name: string;
    game: string;
    mode: string;
    date_start: number;
    date_end: number;
    is_squad: boolean;
    registrations_open: boolean;
    description: string;
    logo: string | null;
    url: string | null;
    registration_deadline: number;
    min_squad_size: number | null;
    max_squad_size: number | null;
    ruleset: string;
    organizer: string | null;
    location: string | null;
    series_id: number | null;
    series_name: string | null;
    series_url: string | null;
    series_description: string | null;
    teams_allowed: boolean;
}