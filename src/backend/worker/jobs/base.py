from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, TypeVar

from common.data.commands import GetJobStateCommand, UpdateJobStateCommand


T = TypeVar('T')

class Job(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def delay(self) -> timedelta:
        pass

    @abstractmethod
    async def run(self):
        pass
    
    async def get_state(self, state_type: type[T] = str) -> T | None:
        from worker.data import handle
        return await handle(GetJobStateCommand(job_name=self.name, state_type=state_type))
    
    async def update_state(self, state: Any) -> None:
        from worker.data import handle
        await handle(UpdateJobStateCommand(job_name=self.name, state=state))