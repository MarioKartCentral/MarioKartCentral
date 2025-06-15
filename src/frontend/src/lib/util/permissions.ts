import type { UserInfo } from '$lib/types/user-info';
import type { Permission } from '$lib/types/permission';

function find_permission(permissions: Permission[], permission_name: string) {
  // if we have a denied permission, always return false
  const denied_perm = permissions.find((p) => p.name === permission_name && p.is_denied);
  if (denied_perm) return false;
  const accepted_perm = permissions.find((p) => p.name === permission_name && !p.is_denied);
  if (accepted_perm) return true;
  return null;
}

function find_user_permission(user_info: UserInfo, permission: string) {
  const permissions: Permission[] = [];
  for (const role of user_info.user_roles) {
    permissions.push(...role.permissions);
  }
  return find_permission(permissions, permission);
}

function find_team_permission(user_info: UserInfo, permission: string, team_id: number) {
  const team_roles = user_info.team_roles.filter((r) => r.team_id === team_id);
  const permissions: Permission[] = [];
  for (const role of team_roles) {
    permissions.push(...role.permissions);
  }
  return find_permission(permissions, permission);
}

function find_series_permission(user_info: UserInfo, permission: string, series_id: number | null) {
  const series_roles = user_info.series_roles.filter((r) => r.series_id === series_id);
  const permissions: Permission[] = [];
  for (const role of series_roles) {
    permissions.push(...role.permissions);
  }
  return find_permission(permissions, permission);
}

function find_tournament_permission(user_info: UserInfo, permission: string, tournament_id: number) {
  const tournament_roles = user_info.tournament_roles.filter((r) => r.tournament_id === tournament_id);
  const permissions: Permission[] = [];
  for (const role of tournament_roles) {
    permissions.push(...role.permissions);
  }
  return find_permission(permissions, permission);
}

export function check_permission(user_info: UserInfo, permission: string, check_denied_only: boolean = false) {
  const found_permission = find_user_permission(user_info, permission);
  if (found_permission === null) {
    return check_denied_only;
  }
  return found_permission;
}

export function check_team_permission(
  user_info: UserInfo,
  permission: string,
  team_id: number,
  check_denied_only: boolean = false,
) {
  const user_permission = find_user_permission(user_info, permission);
  if (user_permission !== null) {
    return user_permission;
  }
  const team_permission = find_team_permission(user_info, permission, team_id);
  if (team_permission === null) {
    return check_denied_only;
  }
  return team_permission;
}

export function check_series_permission(
  user_info: UserInfo,
  permission: string,
  series_id: number | null,
  check_denied_only: boolean = false,
) {
  const user_permission = find_user_permission(user_info, permission);
  if (user_permission !== null) {
    return user_permission;
  }
  const series_permission = find_series_permission(user_info, permission, series_id);
  if (series_permission === null) {
    return check_denied_only;
  }
  return series_permission;
}

export function check_tournament_permission(
  user_info: UserInfo,
  permission: string,
  tournament_id: number,
  series_id: number | null = null,
  check_denied_only: boolean = false,
) {
  const user_permission = find_user_permission(user_info, permission);
  if (user_permission !== null) {
    return user_permission;
  }
  if (series_id) {
    const series_permission = find_series_permission(user_info, permission, series_id);
    if (series_permission !== null) {
      return series_permission;
    }
  }
  const tournament_permission = find_tournament_permission(user_info, permission, tournament_id);
  if (tournament_permission === null) {
    return check_denied_only;
  }
  return tournament_permission;
}

export function get_highest_role_position(user_info: UserInfo) {
  const role_positions = user_info.user_roles.map((r) => r.position);
  return Math.min(...role_positions);
}

export function get_highest_team_role_position(user_info: UserInfo, team_id: number) {
  // if we have the manage team roles permission we can edit any roles in the hierarchy
  if (check_permission(user_info, team_permissions.manage_team_roles)) {
    return -1;
  }
  const team_roles = user_info.team_roles.filter((r) => r.team_id === team_id);
  const role_positions = team_roles.map((r) => r.position);
  return Math.min(...role_positions);
}

export function get_highest_series_role_position(user_info: UserInfo, series_id: number) {
  // if we have the manage series roles permission we can edit any roles in the hierarchy
  if (check_permission(user_info, series_permissions.manage_series_roles)) {
    return -1;
  }
  const series_roles = user_info.series_roles.filter((r) => r.series_id === series_id);
  const role_positions = series_roles.map((r) => r.position);
  return Math.min(...role_positions);
}

export function get_highest_tournament_role_position(
  user_info: UserInfo,
  tournament_id: number,
  series_id: number | null = null,
) {
  // if we have series permissions to edit tournament roles, we can edit any roles in the hierarchy
  if (series_id) {
    if (check_series_permission(user_info, tournament_permissions.manage_tournament_roles, series_id)) {
      return -1;
    }
  } else if (check_permission(user_info, tournament_permissions.manage_tournament_roles)) {
    return -1;
  }
  const tournament_roles = user_info.tournament_roles.filter((r) => r.tournament_id === tournament_id);
  const role_positions = tournament_roles.map((r) => r.position);
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
  create_team: 'team_create',
  join_team: 'team_join',
  invite_to_team: 'team_invite',
  edit_profile: 'profile_edit',
  link_discord: 'discord_link',
  manage_shadow_players: 'shadow_players_manage',
  merge_players: 'player_merge',
  merge_teams: 'team_merge',
  manage_word_filter: 'word_filter_manage',
  edit_user: 'user_edit',
  manage_posts: 'post_manage',
  view_alt_flags: 'alt_flag_view',
  view_user_logins: 'user_logins_view',
  view_basic_ip_info: 'ip_basic_info_view',
  view_ip_addresses: 'ip_address_view',
  view_fingerprints: 'fingerprints_view',
  create_db_backups: 'db_backup_create',
  submit_time_trial: 'time_trial_submit',
  validate_time_trial_proof: 'time_trial_proof_validate',
};

export const team_permissions = {
  edit_team_name_tag: 'team_name_tag_edit',
  edit_team_info: 'team_info_edit',
  create_rosters: 'roster_create',
  manage_rosters: 'roster_manage',
  manage_team_roles: 'team_roles_manage',
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
  manage_series_posts: 'series_posts_manage',
  view_hidden_series: 'series_view_hidden',
};

export const tournament_permissions = {
  edit_tournament: 'tournament_edit',
  manage_tournament_registrations: 'tournament_registrations_manage',
  register_tournament: 'tournament_register',
  register_host: 'tournament_register_host',
  manage_placements: 'tournament_placements_manage',
  manage_tournament_roles: 'tournament_roles_manage',
  view_hidden_tournament: 'tournament_view_hidden',
  manage_tournament_posts: 'tournament_posts_manage',
};

export const mod_panel_permissions = [
  permissions.edit_player,
  permissions.manage_teams,
  permissions.manage_transfers,
  permissions.ban_player,
  permissions.manage_user_roles,
  permissions.edit_player,
  permissions.manage_shadow_players,
  permissions.merge_players,
  permissions.merge_teams,
  permissions.view_alt_flags,
];
