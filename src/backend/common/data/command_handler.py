from types import TracebackType
from common.data.models import Problem
from common.data.commands import Command, SaveToCommandLogCommand, needs_command_log
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper, S3WrapperManager

class CommandHandler:
    def __init__(self, db_path: str, aws_secret_access_key: str, aws_access_key_id: str, aws_endpoint_url: str) -> None:
        self._db_wrapper = DBWrapper(db_path)
        self._s3_wrapper_manager = S3WrapperManager(str(aws_secret_access_key), aws_access_key_id, aws_endpoint_url)
        self._s3_wrapper : S3Wrapper | None = None # type: ignore

    async def __aenter__(self):
        self._s3_wrapper = await self._s3_wrapper_manager.__aenter__() 
        return self
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        if self._s3_wrapper is not None:
            await self._s3_wrapper_manager.__aexit__(exc_type, exc_val, exc_tb)
        self._s3_wrapper = None

    async def handle[T](self, command: Command[T]) -> T:
        if self._s3_wrapper is None:
            raise Problem("Command used before handler initialised")
        resp = await command.handle(self._db_wrapper, self._s3_wrapper)
        if needs_command_log(type(command)):
            await SaveToCommandLogCommand(command).handle(self._db_wrapper, self._s3_wrapper)
        return resp
    
        