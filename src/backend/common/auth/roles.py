from common.auth import permissions

SUPER_ADMINISTRATOR = "Super Administrator"
ADMINISTRATOR = "Administrator"

default_roles_by_id = {
    0: SUPER_ADMINISTRATOR,
    1: ADMINISTRATOR
}

id_by_default_role = { v: k for k, v in default_roles_by_id.items() }

default_permissions_by_default_role = {
    SUPER_ADMINISTRATOR: [ permissions.READ_S3, permissions.WRITE_S3, permissions.WRITE_REDIS, permissions.CREATE_TOURNAMENT, permissions.EDIT_TOURNAMENT, permissions.CREATE_SERIES,
                          permissions.EDIT_SERIES, permissions.CREATE_TOURNAMENT_TEMPLATE, permissions.EDIT_TOURNAMENT_TEMPLATE, permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
                          permissions.EDIT_PLAYER, permissions.MANAGE_TEAMS, permissions.MANAGE_TRANSFERS],
    ADMINISTRATOR: [ permissions.READ_S3, permissions.WRITE_S3, permissions.WRITE_REDIS ],
}

default_role_permission_ids = []
for role, role_perms in default_permissions_by_default_role.items():
    for permission in role_perms:
        default_role_permission_ids += [(id_by_default_role[role], permissions.id_by_permissions[permission])]