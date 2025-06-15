"""
Central command handler coordinating database and S3 operations.
"""

from types import TracebackType
from typing import Dict
import os
import pathlib
import logging

from common.data.models import Problem
from common.data.commands import Command, SaveToCommandLogCommand, needs_command_log
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper, S3WrapperManager
from common.data.duckdb.wrapper import DuckDBWrapper
from opentelemetry import trace

logger = logging.getLogger(__name__)


class CommandHandler:
    def __init__(self, db_paths: Dict[str, str], db_directory: str, s3_secret_key: str, s3_access_key: str, s3_endpoint: str) -> None:
        # Setup DuckDB database
        duckdb_dir = os.path.join(db_directory, "duckdb")
        pathlib.Path(duckdb_dir).mkdir(parents=True, exist_ok=True)
        duckdb_path = os.path.join(duckdb_dir, "time_trials.duckdb")
        
        logger.info(f"Initializing command handler with DuckDB at {duckdb_path}")
        
        # Initialize database wrappers
        self._db_wrapper = DBWrapper(db_paths, DuckDBWrapper(duckdb_path))
        
        # Initialize S3 wrapper manager  
        self._s3_wrapper_manager = S3WrapperManager(str(s3_secret_key), s3_access_key, s3_endpoint)
        self._s3_wrapper: S3Wrapper | None = None
        
        # Initialize telemetry
        self._tracer = trace.get_tracer(__name__)

    async def __aenter__(self):
        self._s3_wrapper = await self._s3_wrapper_manager.__aenter__()
        return self
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        if self._s3_wrapper is not None:
            await self._s3_wrapper_manager.__aexit__(exc_type, exc_val, exc_tb)
        self._s3_wrapper = None

    async def handle[T](self, command: Command[T]) -> T:
        if self._s3_wrapper is None:
            raise Problem("Command handler used before initialization", status=500)

        command_type = type(command).__name__
        with self._tracer.start_as_current_span(f"CommandHandler.handle: {command_type}"):
            resp = await command.handle(self._db_wrapper, self._s3_wrapper)
        if needs_command_log(type(command)):
            await SaveToCommandLogCommand(command).handle(self._db_wrapper, self._s3_wrapper)
        return resp

