import { getContext } from 'svelte';

export function addPermission(permission: string) {
  const ctx: any = getContext('page-init');
  ctx.addPermission(permission);
}

export function setTeamPerms() {
  const ctx: any = getContext('page-init');
  ctx.checkTeamPerms();
}

export function setSeriesPerms() {
  const ctx: any = getContext('page-init');
  ctx.checkSeriesPerms();
}

export const permissions = {
  create_tournament: 'tournament_create',
  edit_tournament: 'tournament_edit',
  create_series: 'series_create',
  edit_series: 'series_edit',
  create_tournament_template: 'tournament_template_create',
  edit_tournament_template: 'tournament_template_edit',
  manage_tournament_registrations: 'tournament_registrations_manage',
  edit_player: 'player_edit',
  manage_teams: 'team_manage',
  invite_team_players: 'team_player_invite',
  manage_team_rosters: 'team_roster_manage',
  edit_team_info: 'team_info_edit',
  manage_registration_history: 'registration_history_edit',
  manage_transfers: 'transfers_manage',
  register_team_tournament: 'team_tournament_register',
  ban_player: 'player_ban',
};

export const team_permissions = {
  edit_team_name_tag: 'team_name_tag_edit',
  edit_team_info: 'team_info_edit',
  create_rosters: 'roster_create',
  manage_rosters: 'roster_manage',
  manage_roles: 'role_manage',
  invite_players: 'player_invite',
  kick_players: 'player_kick',
  register_tournament: 'tournament_register',
  manage_tournament_rosters: 'tournament_rosters_manage',
};

export const series_permissions = {
  create_tournament: "tournament_create",
  edit_tournament: "tournament_edit",
  create_tournament_template: "tournament_template_create",
  edit_tournament_template: "tournament_template_edit",
  manage_tournament_registrations: "tournament_registrations_manage",
  manage_series_roles: "series_roles_manage",
  edit_series: "series_edit"
};

export const mod_panel_permissions = [
  permissions.edit_player,
  permissions.manage_teams,
  permissions.manage_transfers,
  permissions.ban_player,
];

export const valid_games: { [key: string]: string } = {
  mk8dx: 'Mario Kart 8 Deluxe',
  mkw: 'Mario Kart Wii',
  mkt: 'Mario Kart Tour',
};
export const valid_modes: { [key: string]: string[] } = { mk8dx: ['150cc', '200cc'], mkw: ['rt', 'ct'], mkt: ['vsrace'] };
export const mode_names: { [key: string]: string } = {
  '150cc': '150cc',
  '200cc': '200cc',
  rt: 'Regular Tracks',
  ct: 'Custom Tracks',
  vsrace: 'VS Race',
};