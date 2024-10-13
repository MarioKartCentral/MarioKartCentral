export type PlayerNameChangeRequest = {
    id: number;
    player_id: number;
    player_name: string;
    player_country: string;
    request_name: string;
    date: number;
    approval_status: string;
}