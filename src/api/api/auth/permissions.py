READ_S3 = "s3_read"
WRITE_S3 = "s3_write"
WRITE_REDIS = "redis_write"
CREATE_TOURNAMENT = "tournament_create"
EDIT_TOURNAMENT = "tournament_edit"
CREATE_SERIES = "series_create"
EDIT_SERIES = "series_edit"
CREATE_TOURNAMENT_TEMPLATE = "tournament_template_create"
EDIT_TOURNAMENT_TEMPLATE = "tournament_template_edit"

permissions_by_id = {
    0: READ_S3,
    1: WRITE_S3,
    2: WRITE_REDIS,
    3: CREATE_TOURNAMENT,
    4: EDIT_TOURNAMENT,
    5: CREATE_SERIES,
    6: EDIT_SERIES,
    7: CREATE_TOURNAMENT_TEMPLATE,
    8: EDIT_TOURNAMENT_TEMPLATE
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }