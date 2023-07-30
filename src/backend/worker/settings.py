import os

def get_env_or_fail(env_name):
    val = os.getenv(env_name)
    if val is None:
        raise Exception(f"Environment Variable {env_name} is not set")
    return val


DEBUG = os.getenv('DEBUG', "False").lower() == "true"
AWS_ACCESS_KEY_ID = get_env_or_fail("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = get_env_or_fail("S3_SECRET_KEY")
AWS_ENDPOINT_URL = get_env_or_fail("S3_ENDPOINT")
DB_PATH = get_env_or_fail("DB_PATH")
