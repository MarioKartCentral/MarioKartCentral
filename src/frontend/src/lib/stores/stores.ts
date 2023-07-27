import { writable } from 'svelte/store';
import type { UserInfo } from "$lib/types/user-info";

export const user = writable<UserInfo>({id:null, player_id: null, name: null, country_code: null, 
    is_hidden: null, is_shadow: null, is_banned: null, discord_id: null, is_checked: false});

export const have_unread_notification = writable<boolean>(false);
