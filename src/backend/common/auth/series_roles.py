from common.auth import series_permissions, tournament_permissions

ADMINISTRATOR = "Administrator"
ORGANIZER = "Organizer"
HOST_BANNED = "Host Banned"
BANNED = "Banned"

# (roleid, name, role hierarchy pos)
default_roles = [
    (0, ADMINISTRATOR, 0),
    (1, ORGANIZER, 1),
    (2, HOST_BANNED, 99),
    (3, BANNED, 99)
]

id_by_default_role = { name: roleid for roleid, name, pos in default_roles} # type: ignore

default_permissions_by_default_role: dict[str, list[str]] = {
    ADMINISTRATOR: [ 
        series_permissions.CREATE_TOURNAMENT,
        series_permissions.CREATE_TOURNAMENT_TEMPLATE, 
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES
    ],
    ORGANIZER: [
        series_permissions.CREATE_TOURNAMENT_TEMPLATE, 
        series_permissions.EDIT_TOURNAMENT_TEMPLATE,
        series_permissions.MANAGE_SERIES_ROLES,
        tournament_permissions.EDIT_TOURNAMENT, 
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_PLACEMENTS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES
    ],
    HOST_BANNED: [],
    BANNED: []
}

default_denied_permissions_by_default_role: dict[str, list[str]] = {
    ADMINISTRATOR: [],
    ORGANIZER: [],
    HOST_BANNED: [
        tournament_permissions.REGISTER_HOST
    ],
    BANNED:
    [
        tournament_permissions.REGISTER_TOURNAMENT,
        tournament_permissions.REGISTER_HOST
    ]
}

# roleid, permissionid, is_denied
default_role_permission_ids: list[tuple[int, int, bool]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], series_permissions.id_by_permissions[permission], False)]

for role, role_perms in default_denied_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], series_permissions.id_by_permissions[permission], True)]