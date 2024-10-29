type PlayerBasic = {
    id: number;
    name: string;
    country_code: string;
}

export type PlayerClaim = {
    id: number;
    date: number;
    approval_status: string;
    player: PlayerBasic;
    claimed_player: PlayerBasic;
}