from common.auth import tournament_permissions

CREATE_TOURNAMENT = "tournament_create"
CREATE_TOURNAMENT_TEMPLATE = "tournament_template_create"
EDIT_TOURNAMENT_TEMPLATE = "tournament_template_edit"
MANAGE_SERIES_ROLES = "series_roles_manage"
EDIT_SERIES = "series_edit"
MANAGE_SERIES_POSTS = "series_posts_manage"

permissions_by_id = {
    0: CREATE_TOURNAMENT,
    1: CREATE_TOURNAMENT_TEMPLATE,
    2: EDIT_TOURNAMENT_TEMPLATE,
    3: MANAGE_SERIES_ROLES,
    4: EDIT_SERIES,
    5: tournament_permissions.EDIT_TOURNAMENT,
    6: tournament_permissions.MANAGE_TOURNAMENT_REGISTRATIONS,
    7: tournament_permissions.REGISTER_TOURNAMENT,
    8: tournament_permissions.REGISTER_HOST,
    9: tournament_permissions.MANAGE_PLACEMENTS,
    10: tournament_permissions.MANAGE_TOURNAMENT_ROLES,
    11: tournament_permissions.VIEW_HIDDEN_TOURNAMENT,
    12: MANAGE_SERIES_POSTS,
    13: tournament_permissions.MANAGE_TOURNAMENT_POSTS,
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }