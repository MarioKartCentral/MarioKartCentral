import type { PlayerBasic } from "./player-basic";

export type SessionMatchUser = {
    user_id: number;
    date_earliest: number;
    date_latest: number;
    player_info: PlayerBasic;
    is_banned: boolean;
}

export type SessionMatch = {
    date: number;
    users: SessionMatchUser[];
}

export type SessionMatchList = {
    session_matches: SessionMatch[];
    match_count: number;
    page_count: number;
}