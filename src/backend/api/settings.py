from starlette.datastructures import Secret
from starlette.config import Config


config = Config()

DEBUG = config('DEBUG', cast=bool, default=False)
RESET_DATABASE = config('RESET_DATABASE', cast=bool, default=False)
AWS_ACCESS_KEY_ID = config("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = config("S3_SECRET_KEY", cast=Secret)
AWS_ENDPOINT_URL = config("S3_ENDPOINT")
ADMIN_EMAIL = config("API_ADMIN_EMAIL")
ADMIN_PASSWORD = config("API_ADMIN_PASSWORD", cast=Secret)
DB_PATH = config("DB_PATH")
ENV = config("ENV", default=None)