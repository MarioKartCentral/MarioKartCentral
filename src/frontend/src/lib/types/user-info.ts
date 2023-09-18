import type { PlayerInfo } from '$lib/types/player-info';

type ModNotifications = {
  pending_teams: number;
};

type TeamPermissions = {
  team_id: number;
  permissions: string[];
}

type SeriesPermissions = {
  series_id: number;
  permissions: string[];
}

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  player: PlayerInfo | null;
  permissions: string[];
  team_permissions: TeamPermissions[];
  series_permissions: SeriesPermissions[];
  mod_notifications: ModNotifications | null;
  is_checked: boolean;
};
