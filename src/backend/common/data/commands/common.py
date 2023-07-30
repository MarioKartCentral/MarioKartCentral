
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Set, Type, TypeVar

from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper


_TCommandResponse = TypeVar('_TCommandResponse', covariant=True)
class Command(ABC, Generic[_TCommandResponse]):
    @abstractmethod
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> _TCommandResponse:
        pass

_command_log_types: Set[Type[Command[Any]]] = set()
_command_log_type_lookup: Dict[str, Type[Command[Any]]] = {}

_TCommand = TypeVar('_TCommand', bound=Type[Command[Any]])
def save_to_command_log(cls: _TCommand) -> _TCommand:
    _command_log_types.add(cls)
    _command_log_type_lookup[cls.__name__] = cls
    return cls

def needs_command_log(type: Type[Command[Any]]):
    return type in _command_log_types

def get_command_log_type(name: str):
    return _command_log_type_lookup.get(name)