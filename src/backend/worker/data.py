from typing import Dict
from common.data.command_handler import CommandHandler
from common.data.commands import Command
from common.data.db.utils import get_db_paths
from worker import settings

db_paths: Dict[str, str] = get_db_paths(settings.DB_DIRECTORY)

_command_handler = CommandHandler(db_paths, str(settings.S3_SECRET_KEY), settings.S3_ACCESS_KEY, settings.S3_ENDPOINT)

async def handle[T](command: Command[T]) -> T:
    return await _command_handler.handle(command)

async def on_startup():
    await _command_handler.__aenter__()

async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)