import type { FriendCode } from "$lib/types/friend-code";
import type { BanInfo } from "$lib/types/ban-info";

type User = {
    id: number;
    player_id: number | null;
}

export type PlayerInfo = {
    id: number;
    name: string;
    country_code: string | null;
    is_hidden: boolean;
    is_shadow: boolean;
    is_banned: boolean;
    discord_id: string | null;
    friend_codes: FriendCode[];
    user: User;
    ban_info: BanInfo | null;
}