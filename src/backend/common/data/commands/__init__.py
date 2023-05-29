from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper


TCommandResponse = TypeVar('TCommandResponse', covariant=True)
class Command(ABC, Generic[TCommandResponse]):
    @abstractmethod
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> TCommandResponse:
        pass

# re-export all the commands
from .auth import *
from .db_admin import *
from .friend_codes import *
from .notifications import *
from .players import *
from .s3 import *
from .squads import *
from .teams import *
from .tournament_registrations import *
from .tournament_series import *
from .tournament_templates import *
from .tournaments import *
from .user_settings import *
from .users import *