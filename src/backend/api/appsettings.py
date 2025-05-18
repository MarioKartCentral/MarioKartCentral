from starlette.datastructures import Secret
from starlette.config import Config


config = Config()

DEBUG = config("DEBUG", cast=bool, default=False)
RESET_DATABASE = config("RESET_DATABASE", cast=bool, default=False)
S3_ACCESS_KEY = config("S3_ACCESS_KEY")
S3_SECRET_KEY = config("S3_SECRET_KEY", cast=Secret)
S3_ENDPOINT = config("S3_ENDPOINT")
ADMIN_EMAIL = config("API_ADMIN_EMAIL")
ADMIN_PASSWORD = config("API_ADMIN_PASSWORD", cast=Secret)
DISCORD_CLIENT_ID = config("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = config("DISCORD_CLIENT_SECRET", cast=Secret)
ENABLE_IP_LOGGING = config("ENABLE_IP_LOGGING", cast=bool)
DB_DIRECTORY = config("DB_DIRECTORY")
ENV = config("ENV", default=None)
ENABLE_DISCORD = config("ENABLE_DISCORD", cast=bool, default=True)
DISCORD_OAUTH_CALLBACK = config("DISCORD_OAUTH_CALLBACK")
MKC_EMAIL_ADDRESS = config("MKC_EMAIL_ADDRESS")
MKC_EMAIL_HOSTNAME = config("MKC_EMAIL_HOSTNAME")
MKC_EMAIL_PORT = config("MKC_EMAIL_PORT", cast=int)
SITE_URL = config("SITE_URL")
AWS_SES_REGION = config("AWS_SES_REGION", default="us-east-1")
AWS_SES_ACCESS_KEY = config("AWS_SES_ACCESS_KEY", default=None)
AWS_SES_SECRET_KEY = config("AWS_SES_SECRET_KEY", cast=Secret, default=None)
USE_SES_FOR_EMAILS = config("USE_SES_FOR_EMAILS", cast=bool, default=False)