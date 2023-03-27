from api import settings
from common.data.commands import *
from common.data.db import DBWrapper
from common.data.redis import RedisWrapper
from common.data.s3 import S3Wrapper

db_wrapper = DBWrapper(settings.DB_PATH)
s3_wrapper = S3Wrapper(settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ACCESS_KEY_ID, settings.AWS_ENDPOINT_URL)
redis_wrapper = RedisWrapper(settings.REDIS_URL)

async def handle_command(command: Command[TCommandResponse]) -> TCommandResponse:
    return await command.handle(db_wrapper, s3_wrapper)

connect_db = db_wrapper.connect
create_s3_client = s3_wrapper.create_client
redis_conn = redis_wrapper.connect()

async def init_db():
    if settings.RESET_DATABASE:
        await handle_command(ResetDbCommand())
    await handle_command(InitializeDbSchemaCommand())

    from api.auth import pw_hasher
    hashed_pw = pw_hasher.hash(str(settings.ADMIN_PASSWORD))
    await handle_command(SeedDatabaseCommand(settings.ADMIN_EMAIL, hashed_pw))

async def init_s3():
    await handle_command(InitializeS3BucketsCommand())