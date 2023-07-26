import type { RosterPlayer } from "./roster-player";

export type TeamRoster = {
    id: number;
    team_id: number;
    game: string;
    mode: string;
    name: string;
    tag: string;
    creation_date: number;
    is_recruiting: boolean;
    is_approved: string;
    players: RosterPlayer[];
}