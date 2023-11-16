CREATE_TOURNAMENT = "tournament_create"
EDIT_TOURNAMENT = "tournament_edit"
CREATE_TOURNAMENT_TEMPLATE = "tournament_template_create"
EDIT_TOURNAMENT_TEMPLATE = "tournament_template_edit"
MANAGE_TOURNAMENT_REGISTRATIONS = "tournament_registrations_manage"
MANAGE_SERIES_ROLES = "series_roles_manage"
EDIT_SERIES = "series_edit"

permissions_by_id = {
    0: CREATE_TOURNAMENT,
    1: EDIT_TOURNAMENT,
    2: CREATE_TOURNAMENT_TEMPLATE,
    3: EDIT_TOURNAMENT_TEMPLATE,
    4: MANAGE_TOURNAMENT_REGISTRATIONS,
    5: MANAGE_SERIES_ROLES,
    6: EDIT_SERIES
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }