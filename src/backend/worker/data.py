from common.data.command_handler import CommandHandler
from common.data.commands import Command
from worker import settings

_command_handler = CommandHandler(settings.DB_PATH, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_ACCESS_KEY_ID, settings.AWS_ENDPOINT_URL)

async def handle[T](command: Command[T]) -> T:
    return await _command_handler.handle(command)

async def on_startup():
    await _command_handler.__aenter__()

async def on_shutdown():
    await _command_handler.__aexit__(None, None, None)