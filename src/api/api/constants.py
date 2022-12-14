import os

AWS_ACCESS_KEY_ID = os.environ["S3_ACCESS_KEY"]
AWS_SECRET_ACCESS_KEY = os.environ["S3_SECRET_KEY"]
AWS_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
ADMIN_EMAIL = os.environ["API_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["API_ADMIN_PASSWORD"]
REDIS_URL = os.environ["REDIS_URL"]

DB_PATH = "/var/lib/mkc-api/data/mkc.db"
