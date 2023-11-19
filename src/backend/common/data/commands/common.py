
from abc import ABC, abstractmethod
from typing import Any

from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper


class Command[T](ABC):
    @abstractmethod
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> T:
        pass

_command_log_types: set[type[Command[Any]]] = set()
_command_log_type_lookup: dict[str, type[Command[Any]]] = {}

def save_to_command_log[T: type[Command[Any]]](cls: T) -> T:
    _command_log_types.add(cls)
    _command_log_type_lookup[cls.__name__] = cls
    return cls

def needs_command_log(type: type[Command[Any]]):
    return type in _command_log_types

def get_command_log_type(name: str):
    return _command_log_type_lookup.get(name)