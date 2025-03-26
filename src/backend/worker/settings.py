import os

def get_env_or_fail(env_name: str):
    val = os.getenv(env_name)
    if val is None:
        raise Exception(f"Environment Variable {env_name} is not set")
    return val


DEBUG = os.getenv('DEBUG', "False").lower() == "true"
AWS_ACCESS_KEY_ID = get_env_or_fail("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = get_env_or_fail("S3_SECRET_KEY")
AWS_ENDPOINT_URL = get_env_or_fail("S3_ENDPOINT")
DB_PATH = get_env_or_fail("DB_PATH")
DISCORD_CLIENT_ID = get_env_or_fail("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = get_env_or_fail("DISCORD_CLIENT_SECRET")
MKC_EMAIL_ADDRESS = get_env_or_fail("MKC_EMAIL_ADDRESS")
MKC_EMAIL_HOSTNAME = get_env_or_fail("MKC_EMAIL_HOSTNAME")
MKC_EMAIL_PORT = get_env_or_fail("MKC_EMAIL_PORT")
MKC_EMAIL_USERNAME = get_env_or_fail("MKC_EMAIL_USERNAME")
MKC_EMAIL_PASSWORD = get_env_or_fail("MKC_EMAIL_PASSWORD")