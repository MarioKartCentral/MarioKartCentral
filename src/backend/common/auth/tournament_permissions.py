EDIT_TOURNAMENT = "tournament_edit"
MANAGE_TOURNAMENT_REGISTRATIONS = "tournament_registrations_manage"
REGISTER_TOURNAMENT = "tournament_register"
REGISTER_HOST = "tournament_register_host"
MANAGE_PLACEMENTS = "tournament_placements_manage"
MANAGE_TOURNAMENT_ROLES = "tournament_roles_manage"
VIEW_HIDDEN_TOURNAMENT = "tournament_view_hidden"
MANAGE_TOURNAMENT_POSTS = "tournament_posts_manage"

permissions_by_id = {
    0: EDIT_TOURNAMENT,
    1: MANAGE_TOURNAMENT_REGISTRATIONS,
    2: REGISTER_TOURNAMENT,
    3: REGISTER_HOST,
    4: MANAGE_PLACEMENTS,
    5: MANAGE_TOURNAMENT_ROLES,
    6: VIEW_HIDDEN_TOURNAMENT,
    7: MANAGE_TOURNAMENT_POSTS,
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }