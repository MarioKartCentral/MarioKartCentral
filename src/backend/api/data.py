from typing import TypeVar
from api import settings
from common.auth import pw_hasher
from common.data.commands import *
from common.data.db import DBWrapper
from common.data.redis import RedisWrapper
from common.data.s3 import S3WrapperManager, S3Wrapper

db_wrapper = DBWrapper(settings.DB_PATH)
s3_wrapper_manager = S3WrapperManager(str(settings.AWS_SECRET_ACCESS_KEY), settings.AWS_ACCESS_KEY_ID, settings.AWS_ENDPOINT_URL)
s3_wrapper : S3Wrapper = None # type: ignore
redis_wrapper = RedisWrapper(settings.REDIS_URL)

TCommandResponse = TypeVar('TCommandResponse')
async def handle(command: Command[TCommandResponse]) -> TCommandResponse:
    return await command.handle(db_wrapper, s3_wrapper)

redis_conn = redis_wrapper.connect()

async def init_db():
    if settings.RESET_DATABASE:
        await handle(ResetDbCommand())
    await handle(InitializeDbSchemaCommand())

    hashed_pw = pw_hasher.hash(str(settings.ADMIN_PASSWORD))
    await handle(SeedDatabaseCommand(settings.ADMIN_EMAIL, hashed_pw))

async def init_s3():
    global s3_wrapper
    s3_wrapper = await s3_wrapper_manager.__aenter__()
    await handle(InitializeS3BucketsCommand())

async def close_s3():
    await s3_wrapper_manager.__aexit__(None, None, None)
