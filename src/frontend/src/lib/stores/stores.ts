import { writable } from 'svelte/store';
import type { UserInfo } from '$lib/types/user-info';

export const user = writable<UserInfo>({
  id: null,
  player_id: null,
  player: null,
  permissions: [],
  mod_notifications: null,
  is_checked: false,
});

export const have_unread_notification = writable<boolean>(false);
