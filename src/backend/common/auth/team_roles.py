from common.auth import team_permissions as permissions

MANAGER = "Manager"
LEADER = "Leader"

default_roles_by_id = {
    0: MANAGER,
    1: LEADER,
}

id_by_default_role = { v: k for k, v in default_roles_by_id.items() }

default_permissions_by_default_role = {
    MANAGER: [
        permissions.EDIT_TEAM_NAME_TAG, permissions.EDIT_TEAM_INFO, permissions.CREATE_ROSTERS, permissions.MANAGE_ROSTERS,
        permissions.MANAGE_ROLES, permissions.INVITE_PLAYERS, permissions.KICK_PLAYERS, permissions.REGISTER_TOURNAMENT,
        permissions.MANAGE_TOURNAMENT_ROSTERS
    ],
    LEADER: [
        permissions.MANAGE_ROSTERS, permissions.INVITE_PLAYERS, permissions.KICK_PLAYERS, permissions.REGISTER_TOURNAMENT,
        permissions.MANAGE_TOURNAMENT_ROSTERS
    ]
}

default_role_permission_ids: list[tuple[int, int]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission])]