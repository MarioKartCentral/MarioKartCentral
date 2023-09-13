from typing import TypeVar
from api import settings
from common.auth import pw_hasher
from common.data.command_handler import CommandHandler
from common.data.commands import *
import os

_command_handler = CommandHandler(settings.DB_PATH, str(settings.AWS_SECRET_ACCESS_KEY), settings.AWS_ACCESS_KEY_ID, settings.AWS_ENDPOINT_URL)

_TCommandResponse = TypeVar('_TCommandResponse', covariant=True)
async def handle(command: Command[_TCommandResponse]) -> _TCommandResponse:
    return await _command_handler.handle(command)

async def on_startup():
    await _command_handler.__aenter__()

    # Initialize DB
    if settings.RESET_DATABASE:
        await handle(ResetDbCommand())
    await handle(InitializeDbSchemaCommand())

    # Seed DB
    hashed_pw = pw_hasher.hash(str(settings.ADMIN_PASSWORD))
    await handle(SeedDatabaseCommand(settings.ADMIN_EMAIL, hashed_pw))

    # Initialize S3
    if os.getenv("ENV") == "Development":    
        await handle(InitializeS3BucketsCommand())


async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)