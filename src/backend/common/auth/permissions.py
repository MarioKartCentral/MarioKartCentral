from common.auth import team_permissions, series_permissions, tournament_permissions

CREATE_USER_ROLES = "user_roles_create"
EDIT_USER_ROLES = "user_roles_edit"
MANAGE_USER_ROLES = "user_roles_manage"
EDIT_PLAYER = "player_edit"
BAN_PLAYER = "player_ban"
MANAGE_TEAMS = "team_manage"
MANAGE_REGISTRATION_HISTORY = "registration_history_edit"
MANAGE_TRANSFERS = "transfers_manage"
CREATE_SERIES = "series_create"

permissions_by_id = {
    0: CREATE_USER_ROLES,
    1: EDIT_USER_ROLES,
    2: MANAGE_USER_ROLES,
    3: EDIT_PLAYER,
    4: BAN_PLAYER,
    5: MANAGE_TEAMS,
    6: MANAGE_REGISTRATION_HISTORY,
    7: MANAGE_TRANSFERS,
    8: CREATE_SERIES,
    9: team_permissions.EDIT_TEAM_NAME_TAG,
    10: team_permissions.EDIT_TEAM_INFO,
    11: team_permissions.CREATE_ROSTERS,
    12: team_permissions.MANAGE_ROSTERS,
    13: team_permissions.MANAGE_ROLES,
    14: team_permissions.INVITE_PLAYERS,
    15: team_permissions.KICK_PLAYERS,
    16: team_permissions.REGISTER_TOURNAMENT,
    17: team_permissions.MANAGE_TOURNAMENT_ROSTERS,
    18: series_permissions.CREATE_TOURNAMENT,
    19: series_permissions.CREATE_TOURNAMENT_TEMPLATE,
    20: series_permissions.EDIT_TOURNAMENT_TEMPLATE,
    21: series_permissions.MANAGE_SERIES_ROLES,
    22: series_permissions.EDIT_SERIES,
    23: tournament_permissions.EDIT_TOURNAMENT,
    24: tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
    25: tournament_permissions.REGISTER_TOURNAMENT
}


# READ_S3 = "s3_read"
# WRITE_S3 = "s3_write"
# WRITE_REDIS = "redis_write"
# CREATE_TOURNAMENT = "tournament_create"
# EDIT_TOURNAMENT = "tournament_edit"
# CREATE_SERIES = "series_create"
# EDIT_SERIES = "series_edit"
# CREATE_TOURNAMENT_TEMPLATE = "tournament_template_create"
# EDIT_TOURNAMENT_TEMPLATE = "tournament_template_edit"
# MANAGE_TOURNAMENT_REGISTRATIONS = "tournament_registrations_manage"
# EDIT_PLAYER = "player_edit"
# MANAGE_TEAMS = "team_manage"
# INVITE_TEAM_PLAYERS = "team_player_invite"
# MANAGE_TEAM_ROSTERS = "team_roster_manage"
# EDIT_TEAM_INFO = "team_info_edit"
# MANAGE_REGISTRATION_HISTORY = "registration_history_edit"
# MANAGE_TRANSFERS = "transfers_manage"
# REGISTER_TEAM_TOURNAMENT = "team_tournament_register"
# BAN_PLAYER = "player_ban"

# permissions_by_id = {
#     0: READ_S3,
#     1: WRITE_S3,
#     2: WRITE_REDIS,
#     3: CREATE_TOURNAMENT,
#     4: EDIT_TOURNAMENT,
#     5: CREATE_SERIES,
#     6: EDIT_SERIES,
#     7: CREATE_TOURNAMENT_TEMPLATE,
#     8: EDIT_TOURNAMENT_TEMPLATE,
#     9: MANAGE_TOURNAMENT_REGISTRATIONS,
#     10: EDIT_PLAYER,
#     11: MANAGE_TEAMS,
#     12: INVITE_TEAM_PLAYERS,
#     13: MANAGE_TEAM_ROSTERS,
#     14: MANAGE_REGISTRATION_HISTORY,
#     15: MANAGE_TRANSFERS,
#     16: BAN_PLAYER
# }



id_by_permissions = { v: k for k, v in permissions_by_id.items() }