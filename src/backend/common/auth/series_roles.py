from common.auth import series_permissions as permissions

ADMINISTRATOR = "Administrator"
ORGANIZER = "Organizer"


default_roles_by_id = {
    1: ADMINISTRATOR,
    2: ORGANIZER
}

id_by_default_role = { v: k for k, v in default_roles_by_id.items() }

default_permissions_by_default_role = {
    ADMINISTRATOR: [ 
        permissions.CREATE_TOURNAMENT, permissions.EDIT_TOURNAMENT, 
        permissions.CREATE_TOURNAMENT_TEMPLATE, permissions.EDIT_TOURNAMENT_TEMPLATE,
        permissions.MANAGE_TOURNAMENT_REGISTRATIONS, permissions.MANAGE_SERIES_ROLES
    ],
    ORGANIZER: [
        permissions.EDIT_TOURNAMENT, permissions.CREATE_TOURNAMENT_TEMPLATE, permissions.EDIT_TOURNAMENT_TEMPLATE,
        permissions.MANAGE_TOURNAMENT_REGISTRATIONS
    ]
}

default_role_permission_ids: list[tuple[int, int]] = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission])]