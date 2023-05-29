READ_S3 = "s3_read"
WRITE_S3 = "s3_write"
WRITE_REDIS = "redis_write"
CREATE_TOURNAMENT = "tournament_create"
EDIT_TOURNAMENT = "tournament_edit"
CREATE_SERIES = "series_create"
EDIT_SERIES = "series_edit"
CREATE_TOURNAMENT_TEMPLATE = "tournament_template_create"
EDIT_TOURNAMENT_TEMPLATE = "tournament_template_edit"
MANAGE_TOURNAMENT_REGISTRATIONS = "tournament_registrations_manage"
EDIT_PLAYER = "player_edit"
MANAGE_TEAMS = "team_manage"
INVITE_TEAM_PLAYERS = "team_player_invite"
MANAGE_TEAM_ROSTERS = "team_roster_manage"
EDIT_TEAM_INFO = "team_info_edit"
MANAGE_REGISTRATION_HISTORY = "registration_history_edit"
MANAGE_TRANSFERS = "transfers_manage"
REGISTER_TEAM_TOURNAMENT = "team_tournament_register"

permissions_by_id = {
    0: READ_S3,
    1: WRITE_S3,
    2: WRITE_REDIS,
    3: CREATE_TOURNAMENT,
    4: EDIT_TOURNAMENT,
    5: CREATE_SERIES,
    6: EDIT_SERIES,
    7: CREATE_TOURNAMENT_TEMPLATE,
    8: EDIT_TOURNAMENT_TEMPLATE,
    9: MANAGE_TOURNAMENT_REGISTRATIONS,
    10: EDIT_PLAYER,
    11: MANAGE_TEAMS,
    12: INVITE_TEAM_PLAYERS,
    13: MANAGE_TEAM_ROSTERS,
    14: MANAGE_REGISTRATION_HISTORY,
    15: MANAGE_TRANSFERS
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }