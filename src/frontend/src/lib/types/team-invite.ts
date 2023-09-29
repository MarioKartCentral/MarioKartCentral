export type TeamInvite = {
    invite_id: number;
    date: number;
    team_id: number;
    team_name: string;
    team_tag: string;
    team_color: number;
    roster_id: number;
    roster_name: string | null;
    roster_tag: string | null;
    game: string;
    mode: string;
}