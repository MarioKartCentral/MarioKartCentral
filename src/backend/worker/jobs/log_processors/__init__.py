from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any
from common.data.commands import Command
from common.data.models import CommandLog, HistoricalCommandLogIndexEntry


class LogProcessor(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def delay(self) -> timedelta:
        pass

    @abstractmethod
    async def get_last_update_id(self) -> int | None:
        pass

    @abstractmethod
    async def run_from_start(self, historical_log_index: list[HistoricalCommandLogIndexEntry]):
        pass

    @abstractmethod
    async def process_logs(self, logs: list[CommandLog[Command[Any]]]):
        pass

_log_processors: list[LogProcessor] = []

def get_log_processors() -> list[LogProcessor]:
    from worker.jobs.log_processors.historical_log_backup import HistoricalLogBackupLogProcessor
    global _log_processors
    if not _log_processors:
        _log_processors.append(HistoricalLogBackupLogProcessor())
        pass

    return _log_processors