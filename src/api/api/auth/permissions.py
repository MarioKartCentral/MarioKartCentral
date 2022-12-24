READ_S3 = "s3_read"
WRITE_S3 = "s3_write"
WRITE_REDIS = "redis_write"
CREATE_TOURNAMENT = "tournament_create"

permissions_by_id = {
    0: READ_S3,
    1: WRITE_S3,
    2: WRITE_REDIS,
    3: CREATE_TOURNAMENT
}

id_by_permissions = { v: k for k, v in permissions_by_id.items() }