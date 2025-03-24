from common.auth import tournament_permissions

ORGANIZER = "Organizer"
HOST_BANNED = "Host Banned"
BANNED = "Banned"

# (roleid, name, role hierarchy pos)
default_roles = [
    (0, ORGANIZER, 0),
    (1, HOST_BANNED, 99),
    (2, BANNED, 99)
]

id_by_default_role = { name: roleid for roleid, name, pos in default_roles} # type: ignore

default_permissions_by_default_role: dict[str, list[str]] = {
    ORGANIZER: [
        tournament_permissions.EDIT_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
        tournament_permissions.MANAGE_TOURNAMENT_ROLES,
        tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
        tournament_permissions.MANAGE_TOURNAMENT_POSTS,
    ],
    HOST_BANNED: [],
    BANNED: []
}

default_denied_permissions_by_default_role: dict[str, list[str]] = {
    ORGANIZER: [],
    HOST_BANNED: [
        tournament_permissions.REGISTER_HOST
    ],
    BANNED: [
        tournament_permissions.REGISTER_HOST,
        tournament_permissions.REGISTER_TOURNAMENT
    ]
}

# roleid, permissionid, is_denied
default_role_permission_ids: list[tuple[int, int, bool]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], tournament_permissions.id_by_permissions[permission], False)]

for role, role_perms in default_denied_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], tournament_permissions.id_by_permissions[permission], True)]