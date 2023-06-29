import { writable } from 'svelte/store';
import type { UserInfo } from "$lib/types/user-info";

export const user = writable<UserInfo>({user_id:null, player_id: null, name: null, country_code: null, discord_id: null, is_checked: false});