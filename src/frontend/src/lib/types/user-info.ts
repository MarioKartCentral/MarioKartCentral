import type { PlayerInfo } from '$lib/types/player-info';

type ModNotifications = {
  pending_teams: number;
  pending_team_edits: number;
  pending_transfers: number;
};

export type Permission = {
  name: string;
  is_denied: boolean;
};

type UserRole = {
  id: number;
  name: string;
  position: number;
  expires_on: number | null;
  permissions: Permission[];
}

type TeamRole = UserRole & {
  team_id: number;
}

type SeriesRole = UserRole & {
  series_id: number;
}

type TournamentRole = UserRole & {
  tournament_id: number;
}

// type TeamPermissions = {
//   team_id: number;
//   permissions: Permission[];
// };

// type SeriesPermissions = {
//   series_id: number;
//   permissions: Permission[];
// };

// type TournamentPermissions = {
//   tournament_id: number;
//   permissions: Permission[];
// };

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  player: PlayerInfo | null;
  user_roles: UserRole[];
  team_roles: TeamRole[];
  series_roles: SeriesRole[];
  tournament_roles: TournamentRole[];
  mod_notifications: ModNotifications | null;
  is_checked: boolean;
};
