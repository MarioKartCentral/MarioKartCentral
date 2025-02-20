from api import appsettings
from common.auth import pw_hasher
from common.data.command_handler import CommandHandler
from common.data.commands import *

_command_handler = CommandHandler(appsettings.DB_PATH, str(appsettings.AWS_SECRET_ACCESS_KEY), appsettings.AWS_ACCESS_KEY_ID, appsettings.AWS_ENDPOINT_URL)

async def handle[T](command: Command[T]) -> T:
    return await _command_handler.handle(command)

async def on_startup():
    await _command_handler.__aenter__()

    # Initialize DB
    if appsettings.RESET_DATABASE:
        await handle(ResetDbCommand())
    await handle(UpdateDbSchemaCommand())

    # Seed DB
    hashed_pw = pw_hasher.hash(str(appsettings.ADMIN_PASSWORD))
    await handle(SeedDatabaseCommand(appsettings.ADMIN_EMAIL, hashed_pw))

    # Initialize S3
    if appsettings.ENV == "Development":    
        await handle(InitializeS3BucketsCommand())


async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)