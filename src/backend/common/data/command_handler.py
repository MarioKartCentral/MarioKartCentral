"""
Central command handler coordinating database and S3 operations.
"""

from collections.abc import Callable
from functools import partial
from typing import Any, cast, get_type_hints
import os
import pathlib
import logging
import inspect

from common.data.models import Problem
from common.data.command import Command
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
            db_paths: dict[str, str], 
            db_directory: str, 
            s3_secret_key: str, 
            s3_access_key: str, 
            s3_endpoint: str,
            discord_client_id: str,
            discord_client_secret: str,
            discord_oauth_redirect_uri: str | None = None,
            email_service: EmailService | None = None,
            additional_command_modules: list[str] | None = None) -> None:
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

        self._dependency_resolvers: dict[type, Callable[[], dict[str, Any]]] = {}
        self._additional_command_modules = additional_command_modules or []
        self._modules_loaded = False

    def _ensure_modules_loaded(self):
        """Ensure all command modules are loaded. Safe to call multiple times."""
        if self._modules_loaded:
            return
            
        # Import common commands module (always included)
        __import__("common.data.commands")

        # Import additional command modules if provided
        for module_path in self._additional_command_modules:
            try:
                __import__(module_path)
                logger.info(f"Loaded additional command module: {module_path}")
            except ImportError as e:
                logger.error(f"Failed to import command module {module_path}: {e}")
                raise
        
        self._modules_loaded = True

    def _get_dependency_resolvers(self):
        """Build dependency resolvers for all discovered Command subclasses."""
        self._ensure_modules_loaded()
        
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
        # Load command modules and build resolvers after initialization
        if not self._modules_loaded:
            self._get_dependency_resolvers()
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

        span_attributes = {
            "command.type": command_type.__name__,
            "command.module": command_type.__module__,
        }

        with self._tracer.start_as_current_span(
            f"command.execute: {command_type.__name__}",
            attributes=span_attributes
        ):
            try:
                resp = await command.handle(**kwargs)                
            except Exception:
                # Log the exception for structured logging (span auto-records on exit)
                logger.exception(
                    f"Command {command_type.__name__} failed",
                    extra={
                        "command_type": command_type.__name__,
                        "command_module": command_type.__module__,
                    }
                )
                raise

        return resp

