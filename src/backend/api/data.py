from api import appsettings
from common.auth import pw_hasher
from common.data.command_handler import CommandHandler
from common.data.commands import *
from common.data.db.utils import get_db_paths


db_paths = get_db_paths(appsettings.DB_DIRECTORY)

_command_handler = CommandHandler(
    db_paths,
    appsettings.DB_DIRECTORY,
    str(appsettings.S3_SECRET_KEY),
    appsettings.S3_ACCESS_KEY,
    appsettings.S3_ENDPOINT
)

async def handle[T](command: Command[T]) -> T:
    return await _command_handler.handle(command)

async def on_startup():
    await _command_handler.__aenter__()

    # Initialize DBs
    if appsettings.RESET_DATABASE:
        for db_name in db_paths.keys():
            await handle(ResetDbCommand(db_name=db_name))
    await handle(UpdateDbSchemaCommand())
    
    if appsettings.RESET_DUCK_DB:
        await handle(ResetDuckDbCommand())
    # Initialize DuckDB schema
    await handle(SetupDuckDBSchemaCommand())

    # Seed DB
    hashed_pw = pw_hasher.hash(str(appsettings.ADMIN_PASSWORD))
    await handle(SeedDatabasesCommand(appsettings.ADMIN_EMAIL, hashed_pw))

    # Initialize S3
    if appsettings.ENV == "Development":
        await handle(InitializeS3BucketsCommand())


async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)