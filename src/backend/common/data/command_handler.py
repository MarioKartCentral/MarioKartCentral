"""
Central command handler coordinating database and S3 operations.
"""

from functools import partial
from typing import Any, Callable, Dict, cast, get_type_hints
import os
import pathlib
import logging
import inspect

from common.data.models import Problem
from common.data.command import Command, needs_command_log
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper, S3WrapperManager
from common.data.duckdb.wrapper import DuckDBWrapper
from opentelemetry import trace

from common.discord import DiscordApi
from common.emails import EmailService
from common.ip_api import IPApi

logger = logging.getLogger(__name__)


class CommandHandler:
    def __init__(
            self, 
            db_paths: Dict[str, str], 
            db_directory: str, 
            s3_secret_key: str, 
            s3_access_key: str, 
            s3_endpoint: str,
            discord_client_id: str,
            discord_client_secret: str,
            discord_oauth_redirect_uri: str | None = None,
            email_service: EmailService | None = None) -> None:
        # Setup DuckDB database
        duckdb_dir = os.path.join(db_directory, "duckdb")
        pathlib.Path(duckdb_dir).mkdir(parents=True, exist_ok=True)
        duckdb_path = os.path.join(duckdb_dir, "time_trials.duckdb")
        self._duckdb_wrapper = DuckDBWrapper(duckdb_path)

        logger.info(f"Initializing command handler with DuckDB at {duckdb_path}")
        
        # Initialize database wrappers
        self._db_wrapper = DBWrapper(db_paths)
        
        # Initialize S3 wrapper manager  
        self._s3_wrapper_manager = S3WrapperManager(str(s3_secret_key), s3_access_key, s3_endpoint)
        self._s3_wrapper: S3Wrapper | None = None

        # Initialize discord API
        self._discord_api = DiscordApi(discord_client_id, discord_client_secret, discord_oauth_redirect_uri)

        self._email_service = email_service
        
        # Initialize telemetry
        self._tracer = trace.get_tracer(__name__)

        self._dependency_resolvers: Dict[type, Callable[[], dict[str, Any]]] = {}
        self._get_dependency_resolvers()

    def _get_dependency_resolvers(self):
        # import all commands so that they are registered
        import common.data.commands # pyright: ignore[reportUnusedImport]
        for subclass in cast(list[type[Command[Any]]], Command.__subclasses__()):
            sig = inspect.signature(subclass.handle)
            hints = get_type_hints(subclass.handle)

            def get_s3_wrapper():
                if self._s3_wrapper is None:
                    raise Problem("Command handler used before initialization", status=500)
                return self._s3_wrapper
            
            def get_email_service():
                if self._email_service is None:
                    raise Problem("Email service not configured", status=500)
                return self._email_service
            
            dependencies: dict[str, Callable[[], Any]] = {}
            for name in sig.parameters:
                if name == "self":
                    continue
                expected_type: type = cast(type, hints.get(name))
                if expected_type == DBWrapper:
                    dependencies[name] = lambda: self._db_wrapper
                elif expected_type == S3Wrapper:
                    dependencies[name] = get_s3_wrapper
                elif expected_type == DuckDBWrapper:
                    dependencies[name] = lambda: self._duckdb_wrapper
                elif expected_type == DiscordApi:
                    dependencies[name] = lambda: self._discord_api
                elif expected_type == CommandHandler:
                    dependencies[name] = lambda: self
                elif expected_type == EmailService:
                    dependencies[name] = get_email_service
                elif expected_type == IPApi:
                    dependencies[name] = lambda: IPApi()
                else:
                    raise Problem(f"Cannot resolve dependency for {name}: {expected_type}", status=500)

            def build_kwargs(dependencies: dict[str, Callable[[], Any]]):
                return {name: resolver() for name, resolver in dependencies.items()}
            
            self._dependency_resolvers[subclass] = partial(build_kwargs, dependencies=dependencies)

    async def __aenter__(self):
        self._s3_wrapper = await self._s3_wrapper_manager.__aenter__()
        return self
    
    async def __aexit__(self, *args: Any):
        if self._s3_wrapper is not None:
            await self._s3_wrapper_manager.__aexit__(*args)
        self._s3_wrapper = None

    async def handle[T](self, command: Command[T]) -> T:
        if self._s3_wrapper is None:
            raise Problem("Command handler used before initialization", status=500)
        
        command_type = type(command)
        if command_type not in self._dependency_resolvers:
            raise Problem(f"Unsupported command type: {command_type.__name__}", status=500)
        
        kwargs = self._dependency_resolvers[command_type]()

        with self._tracer.start_as_current_span(f"CommandHandler.handle: {command_type.__name__}"):
            resp = await command.handle(**kwargs)

        if needs_command_log(command_type):
            from common.data.commands import SaveToCommandLogCommand
            await self.handle(SaveToCommandLogCommand(command))

        return resp

