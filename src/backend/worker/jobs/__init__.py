from abc import ABC, abstractmethod
from datetime import timedelta

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

_jobs: list[Job] = []

def get_all_jobs():
    from worker.jobs import log_processor
    if not _jobs:
        _jobs.extend(log_processor.get_jobs())
    return _jobs