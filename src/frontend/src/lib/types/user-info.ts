import type { PlayerInfo } from '$lib/types/player-info';

type ModNotifications = {
  pending_teams: number;
  pending_team_edits: number;
  pending_transfers: number;
};

type Permission = {
  name: string;
  is_denied: boolean;
};

type TeamPermissions = {
  team_id: number;
  permissions: Permission[];
};

type SeriesPermissions = {
  series_id: number;
  permissions: Permission[];
};

type TournamentPermissions = {
  tournament_id: number;
  permissions: Permission[];
};

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  player: PlayerInfo | null;
  permissions: Permission[];
  team_permissions: TeamPermissions[];
  series_permissions: SeriesPermissions[];
  tournament_permissions: TournamentPermissions[];
  mod_notifications: ModNotifications | null;
  is_checked: boolean;
};
