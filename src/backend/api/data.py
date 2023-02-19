from api import settings
from common.data.db import DBWrapper
from common.data.redis import RedisWrapper
from common.data.s3 import S3Wrapper

db_wrapper = DBWrapper(settings.DB_PATH, settings.RESET_DATABASE, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
s3_wrapper = S3Wrapper(settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ACCESS_KEY_ID, settings.AWS_ENDPOINT_URL)
redis_wrapper = RedisWrapper(settings.REDIS_URL)

connect_db = db_wrapper.connect
create_s3_client = s3_wrapper.create_client
redis_conn = redis_wrapper.connect()

async def init_db():
    await db_wrapper.init()

async def init_s3():
    await s3_wrapper.init()