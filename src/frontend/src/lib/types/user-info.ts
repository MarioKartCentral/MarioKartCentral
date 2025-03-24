import type { PlayerInfo } from '$lib/types/player-info';
import type { Permission } from '$lib/types/permission';

type ModNotifications = {
  pending_teams: number;
  pending_team_edits: number;
  pending_transfers: number;
  pending_player_name_changes: number;
  pending_player_claims: number;
};

type UserRole = {
  id: number;
  name: string;
  position: number;
  expires_on: number | null;
  permissions: Permission[];
};

type TeamRole = UserRole & {
  team_id: number;
};

type SeriesRole = UserRole & {
  series_id: number;
};

type TournamentRole = UserRole & {
  tournament_id: number;
};

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  email_confirmed: boolean;
  force_password_reset: boolean;
  player: PlayerInfo | null;
  user_roles: UserRole[];
  team_roles: TeamRole[];
  series_roles: SeriesRole[];
  tournament_roles: TournamentRole[];
  mod_notifications: ModNotifications | null;
  is_checked: boolean;
};
