import type { UserInfo } from '$lib/types/user-info';
import type { Permission } from '$lib/types/permission';

export function check_permission(user_info: UserInfo, permission: string, check_denied_only: boolean = false) {
  const permissions: Permission[] = [];
  for(const role of user_info.user_roles) {
    permissions.push(...role.permissions);
  }
  const accepted_perm = permissions.find((p) => p.name === permission && !p.is_denied);
  // if we have the permission and it isnt denied, return true
  if (accepted_perm) return true;
  // if check_denied_only is true, we only care about the absence of a denied permission
  if (check_denied_only) {
    // if there is no denied permission we return true
    const denied_perm = permissions.find((p) => p.name === permission && p.is_denied);
    if (denied_perm) return false;
    return true;
  }
  return false;
}

export function check_team_permission(
  user_info: UserInfo,
  permission: string,
  team_id: number,
  check_denied_only: boolean = false,
) {
  const team_roles = user_info.team_roles.filter((r) => r.team_id === team_id);
  const permissions: Permission[] = [];
  for(const role of team_roles) {
    permissions.push(...role.permissions);
  }
  if (permissions.length) {
    const accepted_perm = permissions.find((p) => p.name === permission && !p.is_denied);
    if (accepted_perm) return true;
    if (check_denied_only) {
      const denied_perm = permissions.find((p) => p.name === permission && p.is_denied);
      // if we have a denied team permission, it can be overridden by an accepted user permission,
      // so we just run check_permission function with check_denied_only set to false
      if (denied_perm) {
        return check_permission(user_info, permission, false);
      }
    }
  }
  // if we cant find a team permission, check user permissions last
  return check_permission(user_info, permission, check_denied_only);
}

export function check_series_permission(
  user_info: UserInfo,
  permission: string,
  series_id: number | null,
  check_denied_only: boolean = false,
) {
  const series_roles = user_info.series_roles.filter((r) => r.series_id === series_id);
  const permissions: Permission[] = [];
  for(const role of series_roles) {
    permissions.push(...role.permissions);
  }
  if (permissions.length) {
    const accepted_perm = permissions.find((p) => p.name === permission && !p.is_denied);
    if (accepted_perm) return true;
    if (check_denied_only) {
      const denied_perm = permissions.find((p) => p.name === permission && p.is_denied);
      // if we have a denied series permission, it can be overridden by an accepted user permission,
      // so we just run check_permission function with check_denied_only set to false
      if (denied_perm) {
        return check_permission(user_info, permission, false);
      }
    }
  }
  // if we cant find a series permission, check user permissions last
  return check_permission(user_info, permission, check_denied_only);
}

export function check_tournament_permission(
  user_info: UserInfo,
  permission: string,
  tournament_id: number,
  series_id: number | null = null,
  check_denied_only: boolean = false,
) {
  const tournament_roles = user_info.tournament_roles.filter((r) => r.tournament_id === tournament_id);
  const permissions: Permission[] = [];
  for(const role of tournament_roles) {
    permissions.push(...role.permissions);
  }
  if (permissions.length) {
    const accepted_perm = permissions.find((p) => p.name === permission && !p.is_denied);
    if (accepted_perm) return true;
    if (check_denied_only) {
      const denied_perm = permissions.find((p) => p.name === permission && p.is_denied);
      // if we have a denied tournament permission, it can be overridden by an accepted user or series permission,
      // so just run check_series_permission function with check_denied_only set to false
      if (denied_perm) {
        return check_series_permission(user_info, permission, series_id, false);
      }
    }
  }
  return check_series_permission(user_info, permission, series_id, check_denied_only);
}

export function get_highest_role_position(user_info: UserInfo) {
  const role_positions = user_info.user_roles.map((r) => r.position);
  return Math.min(...role_positions);
}

export const permissions = {
  create_user_roles: 'user_roles_create',
  edit_user_roles: 'user_roles_edit',
  manage_user_roles: 'user_roles_manage',
  edit_player: 'player_edit',
  ban_player: 'player_ban',
  manage_teams: 'team_manage',
  manage_registration_history: 'registration_history_edit',
  manage_transfers: 'transfers_manage',
  create_series: 'series_create',
};

export const team_permissions = {
  edit_team_name_tag: 'team_name_tag_edit',
  edit_team_info: 'team_info_edit',
  create_rosters: 'roster_create',
  manage_rosters: 'roster_manage',
  manage_roles: 'team_roles_manage',
  invite_players: 'team_player_invite',
  kick_players: 'team_player_kick',
  register_tournament: 'team_tournament_register',
  manage_tournament_rosters: 'team_tournament_rosters_manage',
};

export const series_permissions = {
  create_tournament: 'tournament_create',
  create_tournament_template: 'tournament_template_create',
  edit_tournament_template: 'tournament_template_edit',
  manage_series_roles: 'series_roles_manage',
  edit_series: 'series_edit',
};

export const tournament_permissions = {
  edit_tournament: 'tournament_edit',
  manage_tournament_registrations: 'tournament_registrations_manage',
  register_tournament: 'tournament_register',
  register_host: 'tournament_register_host',
};

export const mod_panel_permissions = [
  permissions.edit_player,
  permissions.manage_teams,
  permissions.manage_transfers,
  permissions.ban_player,
];
