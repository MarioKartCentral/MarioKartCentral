from common.auth import permissions, team_permissions, series_permissions, tournament_permissions

SUPER_ADMINISTRATOR = "Super Administrator"
ADMINISTRATOR = "Administrator"
SITE_MODERATOR = "Site Moderator"
SUPPORT_STAFF = "Support Staff"
SITE_SUPPORTER = "Site Supporter"
EVENT_ADMIN = "Event Admin"
EVENT_MOD = "Event Mod"
BANNED = "Banned"
TEAM_LEADER_BANNED = "Team Leader Banned"

# (roleid, name, role hierarchy pos)
default_roles = [
    (0, SUPER_ADMINISTRATOR, 0),
    (1, ADMINISTRATOR, 1),
    (2, SITE_MODERATOR, 2),
    (3, EVENT_ADMIN, 3),
    (4, EVENT_MOD, 4),
    (5, SUPPORT_STAFF, 5),
    (6, SITE_SUPPORTER, 6),
    (7, BANNED, 99),
    (8, TEAM_LEADER_BANNED, 99),
]

id_by_default_role = { name: roleid for roleid, name, pos in default_roles} # type: ignore

default_permissions_by_default_role: dict[str, list[str]] = {
    SUPER_ADMINISTRATOR: [
        permissions.CREATE_USER_ROLES, 
        permissions.EDIT_USER_ROLES,
        permissions.MANAGE_USER_ROLES,
        permissions.EDIT_PLAYER,
        permissions.BAN_PLAYER,
        permissions.MANAGE_TEAMS,
        permissions.MANAGE_REGISTRATION_HISTORY,
        permissions.MANAGE_TRANSFERS,
        permissions.CREATE_SERIES,
        permissions.MANAGE_SHADOW_PLAYERS,
        permissions.MERGE_PLAYERS,
        permissions.MERGE_TEAMS,
        permissions.MANAGE_WORD_FILTER,
        permissions.EDIT_USER,
        permissions.IMPORT_V1_DATA,
        permissions.MANAGE_POSTS,
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_TEAM_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        series_permissions.MANAGE_SERIES_POSTS,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
    ],
    ADMINISTRATOR: [
        permissions.CREATE_USER_ROLES, 
        permissions.EDIT_USER_ROLES,
        permissions.MANAGE_USER_ROLES,
        permissions.EDIT_PLAYER,
        permissions.BAN_PLAYER,
        permissions.MANAGE_TEAMS,
        permissions.MANAGE_REGISTRATION_HISTORY,
        permissions.MANAGE_TRANSFERS,
        permissions.CREATE_SERIES,
        permissions.MANAGE_SHADOW_PLAYERS,
        permissions.MERGE_PLAYERS,
        permissions.MERGE_TEAMS,
        permissions.MANAGE_WORD_FILTER,
        permissions.EDIT_USER,
        permissions.MANAGE_POSTS,
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_TEAM_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        series_permissions.MANAGE_SERIES_POSTS,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_POSTS,
    ],
    SITE_MODERATOR: [
        permissions.EDIT_PLAYER,
        permissions.BAN_PLAYER,
        permissions.MANAGE_TEAMS,
        permissions.MANAGE_REGISTRATION_HISTORY,
        permissions.MANAGE_TRANSFERS,
        permissions.CREATE_SERIES,
        permissions.MANAGE_SHADOW_PLAYERS,
        permissions.MANAGE_WORD_FILTER,
        permissions.MANAGE_POSTS,
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_TEAM_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        series_permissions.MANAGE_SERIES_POSTS,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_POSTS,
    ],
    EVENT_ADMIN: [
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        series_permissions.MANAGE_SERIES_POSTS,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_POSTS,
    ],
    EVENT_MOD: [
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
    ],
    SUPPORT_STAFF: [
        permissions.EDIT_PLAYER,
        permissions.MANAGE_TEAMS,
        permissions.MANAGE_REGISTRATION_HISTORY,
        permissions.MANAGE_TRANSFERS,
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_TEAM_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
    ],
    SITE_SUPPORTER: [],
    BANNED: [],
    TEAM_LEADER_BANNED: [],
}

default_denied_permissions_by_default_role: dict[str, list[str]] = {
    SUPER_ADMINISTRATOR: [],
    ADMINISTRATOR: [],
    SITE_MODERATOR: [],
    EVENT_ADMIN: [],
    EVENT_MOD: [],
    SUPPORT_STAFF: [],
    SITE_SUPPORTER: [],
    BANNED: [
        tournament_permissions.REGISTER_TOURNAMENT,
        permissions.CREATE_TEAM,
        permissions.JOIN_TEAM,
        permissions.INVITE_TO_TEAM,
        permissions.EDIT_PROFILE,
        permissions.LINK_DISCORD
    ],
    TEAM_LEADER_BANNED: [
        permissions.CREATE_TEAM,
        permissions.INVITE_TO_TEAM
    ],
}

# roleid, permissionid, is_denied
default_role_permission_ids: list[tuple[int, int, bool]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission], False)]

for role, role_perms in default_denied_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission], True)]