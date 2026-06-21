from common.data.command_handler import CommandHandler
from common.data.command import Command
from common.data.db.utils import get_db_paths
from worker import settings
from common.data.db.db_wrapper import DBWrapper
from common.data.duckdb.wrapper import DuckDBInitialiser
from common.data.s3 import S3WrapperManager
from common.discord import DiscordApi
from common.ip_api import IPApi

db_paths: dict[str, str] = get_db_paths(settings.DB_DIRECTORY)

_command_handler = CommandHandler(
    DBWrapper(db_paths),
    DuckDBInitialiser.get_duckdb_wrapper(settings.DB_DIRECTORY),
    S3WrapperManager(
        settings.S3_SECRET_KEY, settings.S3_ACCESS_KEY,
        settings.S3_REGION, settings.S3_ENDPOINT
    ),
    DiscordApi(
        settings.DISCORD_CLIENT_ID,
        str(settings.DISCORD_CLIENT_SECRET)
    ),
    IPApi(),
    additional_command_modules=["worker.jobs"]
)


async def handle[T](command: Command[T]) -> T:
    return await _command_handler.handle(command)


async def on_startup():
    await _command_handler.__aenter__()


async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)
