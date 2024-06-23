from common.auth import permissions, team_permissions, series_permissions, tournament_permissions
from common.data.models import RolePermission, Role 

SUPER_ADMINISTRATOR = "Super Administrator"
ADMINISTRATOR = "Administrator"
SITE_MODERATOR = "Site Moderator"
SUPPORT_STAFF = "Support Staff"
SITE_SUPPORTER = "Site Supporter"
BANNED = "Banned"

default_roles_by_id = {
    0: SUPER_ADMINISTRATOR,
    1: ADMINISTRATOR,
    2: SITE_MODERATOR,
    3: SUPPORT_STAFF,
    4: SITE_SUPPORTER,
    5: BANNED
}

id_by_default_role = { v: k for k, v in default_roles_by_id.items() }

default_permissions_by_default_role = {
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
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS
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
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS
    ],
    SITE_MODERATOR: [
        permissions.EDIT_PLAYER,
        permissions.BAN_PLAYER,
        permissions.MANAGE_TEAMS,
        permissions.MANAGE_REGISTRATION_HISTORY,
        permissions.MANAGE_TRANSFERS,
        permissions.CREATE_SERIES,
        team_permissions.EDIT_TEAM_NAME_TAG,
        team_permissions.EDIT_TEAM_INFO,
        team_permissions.CREATE_ROSTERS,
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE,
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        series_permissions.EDIT_SERIES,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS
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
        team_permissions.MANAGE_ROLES,
        team_permissions.INVITE_PLAYERS,
        team_permissions.KICK_PLAYERS,
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS,
    ],
    SITE_SUPPORTER: [],
    BANNED: []
}

default_denied_permissions_by_default_role = {
    SUPER_ADMINISTRATOR: [],
    ADMINISTRATOR: [],
    SITE_MODERATOR: [],
    SITE_SUPPORTER: [],
    BANNED: [
        tournament_permissions.REGISTER_TOURNAMENT
    ]
}

default_role_permission_ids: list[tuple[int, int]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission])]

default_role_denied_permission_ids: list[tuple[int, int, bool]] = []
for role, role_perms in default_denied_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_denied_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission], True)]