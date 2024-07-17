import { writable } from 'svelte/store';
import type { UserInfo } from '$lib/types/user-info';

export const user = writable<UserInfo>({
  id: null,
  player_id: null,
  player: null,
  permissions: [],
  team_permissions: [],
  series_permissions: [],
  tournament_permissions: [],
  mod_notifications: null,
  is_checked: false,
});

export const have_unread_notification = writable<number>(0);
