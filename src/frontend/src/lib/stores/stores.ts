import { writable } from 'svelte/store';
import type { UserInfo } from '$lib/types/user-info';

export const user = writable<UserInfo>({
  id: null,
  player_id: null,
  email_confirmed: false,
  force_password_reset: false,
  player: null,
  user_roles: [],
  team_roles: [],
  series_roles: [],
  tournament_roles: [],
  mod_notifications: null,
  is_checked: false,
});

export const have_unread_notification = writable<number>(0);
