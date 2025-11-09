from common.auth import team_permissions

MANAGER = "Manager"
LEADER = "Leader"

# (roleid, name, role hierarchy pos)
default_roles = [
    (0, MANAGER, 0),
    (1, LEADER, 1)
]

id_by_default_role = { name: roleid for roleid, name, _ in default_roles}

default_permissions_by_default_role = {
    MANAGER: [
        team_permissions.EDIT_TEAM_NAME_TAG, 
        team_permissions.EDIT_TEAM_INFO, 
        team_permissions.CREATE_ROSTERS, 
        team_permissions.MANAGE_ROSTERS,
        team_permissions.MANAGE_TEAM_ROLES, 
        team_permissions.INVITE_PLAYERS, 
        team_permissions.KICK_PLAYERS, 
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS
    ],
    LEADER: [
        team_permissions.MANAGE_ROSTERS, 
        team_permissions.INVITE_PLAYERS, 
        team_permissions.KICK_PLAYERS, 
        team_permissions.REGISTER_TOURNAMENT,
        team_permissions.MANAGE_TOURNAMENT_ROSTERS
    ]
}

default_denied_permissions_by_default_role: dict[str, list[str]] = {
    MANAGER: [],
    LEADER: []
}

# roleid, permissionid, is_denied
default_role_permission_ids: list[tuple[int, int, bool]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], team_permissions.id_by_permissions[permission], False)]

for role, role_perms in default_denied_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], team_permissions.id_by_permissions[permission], True)]