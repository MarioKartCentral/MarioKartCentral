import type { PlayerInfo } from '$lib/types/player-info';

type ModNotifications = {
  pending_teams: number;
};

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  player: PlayerInfo | null;
  permissions: string[];
  mod_notifications: ModNotifications | null;
  is_checked: boolean;
};
