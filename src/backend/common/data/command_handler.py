"""
Central command handler coordinating database and S3 operations.
"""

from collections.abc import Callable
from functools import partial
from typing import Any, cast, get_type_hints
import logging
import inspect

from common.data.models import Problem
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper, S3WrapperManager
from common.data.duckdb.wrapper import DuckDBWrapper
from opentelemetry import trace
from common.discord import DiscordService
from common.emails import EmailService
from common.ip_api import IPService

logger = logging.getLogger(__name__)


class CommandHandler:
    _db_wrapper: DBWrapper
    _duckdb_wrapper: DuckDBWrapper
    _s3_wrapper_manager: S3WrapperManager
    _s3_wrapper: S3Wrapper | None = None
    _discord_service: DiscordService
    _ip_service: IPService
    _email_service: EmailService | None = None
    _tracer: trace.Tracer
    _dependency_resolvers: dict[type, Callable[[], dict[str, Any]]]
    _additional_command_modules: list[str]
    __modules_loaded: bool = False

    def __init__(
            self,
            db_wrapper: DBWrapper,
            duckdb_wrapper: DuckDBWrapper,
            s3_wrapper: S3WrapperManager,
            discord_service: DiscordService,
            ip_service: IPService,
            email_service: EmailService | None = None,
            additional_command_modules: list[str] | None = None) -> None:

        self._dependency_resolvers = {}
        self._additional_command_modules = additional_command_modules or []

        # Initialize wrappers and services
        self._db_wrapper = db_wrapper
        self._duckdb_wrapper = duckdb_wrapper
        self._s3_wrapper_manager = s3_wrapper
        self._discord_service = discord_service
        self._ip_service = ip_service
        self._email_service = email_service

        # Initialize telemetry
        self._tracer = trace.get_tracer(__name__)

    def _ensure_modules_loaded(self):
        """Ensure all command modules are loaded. Safe to call multiple times."""
        if self.__modules_loaded:
            return

        # Import common commands module (always included)
        __import__("common.data.commands")

        # Import additional command modules if provided
        for module_path in self._additional_command_modules:
            try:
                __import__(module_path)
                logger.info(f"Loaded additional command module: {module_path}")
            except ImportError as e:
                logger.error(
                    f"Failed to import command module {module_path}: {e}")
                raise

        self.__modules_loaded = True

    def _get_dependency_resolvers(self):
        """Build dependency resolvers for all discovered Command subclasses."""
        self._ensure_modules_loaded()

        for subclass in cast(list[type[Command[Any]]], Command.__subclasses__()):
            sig = inspect.signature(subclass.handle)
            hints = get_type_hints(subclass.handle)

            def get_s3_wrapper():
                if self._s3_wrapper is None:
                    raise Problem(
                        "Command handler used before initialization", status=500)
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
                elif expected_type == DiscordService:
                    dependencies[name] = lambda: self._discord_service
                elif expected_type == CommandHandler:
                    dependencies[name] = lambda: self
                elif expected_type == EmailService:
                    dependencies[name] = get_email_service
                elif expected_type == IPService:
                    dependencies[name] = lambda: self._ip_service
                else:
                    raise Problem(
                        f"Cannot resolve dependency for {name}: {expected_type}", status=500)

            def build_kwargs(dependencies: dict[str, Callable[[], Any]]):
                return {name: resolver() for name, resolver in dependencies.items()}

            self._dependency_resolvers[subclass] = partial(
                build_kwargs, dependencies=dependencies)

    async def __aenter__(self):
        self._s3_wrapper = await self._s3_wrapper_manager.__aenter__()
        # Load command modules and build resolvers after initialization
        if not self.__modules_loaded:
            self._get_dependency_resolvers()
        return self

    async def __aexit__(self, *args: Any):
        if self._s3_wrapper is not None:
            await self._s3_wrapper_manager.__aexit__(*args)
        self._s3_wrapper = None

    async def handle[T](self, command: Command[T]) -> T:
        if self._s3_wrapper is None:
            raise Problem(
                "Command handler used before initialization", status=500)

        command_type = type(command)
        if command_type not in self._dependency_resolvers:
            raise Problem(
                f"Unsupported command type: {command_type.__name__}", status=500)

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
