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

export const mod_panel_permissions = [
  permissions.edit_player,
  permissions.manage_teams,
  permissions.manage_transfers,
  permissions.ban_player,
];
