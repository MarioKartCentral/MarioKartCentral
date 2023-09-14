EDIT_TEAM_NAME_TAG = "team_name_tag_edit"
EDIT_TEAM_INFO = "team_info_edit"
CREATE_ROSTERS = "roster_create"
MANAGE_ROSTERS = "roster_manage"
MANAGE_ROLES = "role_manage"
INVITE_PLAYERS = "player_invite"
KICK_PLAYERS = "player_kick"
REGISTER_TOURNAMENT = "tournament_register"
MANAGE_TOURNAMENT_ROSTERS = "tournament_rosters_manage"

permissions_by_id = {
    0: EDIT_TEAM_NAME_TAG,
    1: EDIT_TEAM_INFO,
    2: CREATE_ROSTERS,
    3: MANAGE_ROSTERS,
    4: MANAGE_ROLES,
    5: INVITE_PLAYERS,
    6: KICK_PLAYERS,
    7: REGISTER_TOURNAMENT,
    8: MANAGE_TOURNAMENT_ROSTERS
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }