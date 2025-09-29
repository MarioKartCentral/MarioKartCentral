from abc import ABC, abstractmethod
from datetime import timedelta
from typing import TypeVar, Type, Optional, Any
from worker.data import handle
from common.data.commands.worker.job_state import GetJobStateCommand, UpdateJobStateCommand

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
    
    async def get_state(self, state_type: Type[T] = str) -> Optional[T]:
        return await handle(GetJobStateCommand(job_name=self.name, state_type=state_type))
    
    async def update_state(self, state: Any) -> None:
        await handle(UpdateJobStateCommand(job_name=self.name, state=state))

_jobs: list[Job] = []

def get_all_jobs():
    from worker.jobs import (
        log_processor, 
        role_checker, 
        discord_refresh, 
        unban_players_checker, 
        ip_check, 
        expired_token_check,
        activity_queue_processor,
        activity_compression,
        vpn_detection,
        ip_match_detection,
        persistent_cookie_detection,
        fingerprint_match_detection,
        db_backup,
        close_tournament_registrations
    )
    if not _jobs:
        # _jobs.extend(log_processor.get_jobs())
        _jobs.extend(role_checker.get_jobs())
        _jobs.extend(discord_refresh.get_jobs())
        _jobs.extend(unban_players_checker.get_jobs())
        _jobs.extend(ip_check.get_jobs())
        _jobs.extend(expired_token_check.get_jobs())
        _jobs.extend(activity_queue_processor.get_jobs())
        _jobs.extend(activity_compression.get_jobs())
        _jobs.extend(vpn_detection.get_jobs())
        _jobs.extend(ip_match_detection.get_jobs())
        _jobs.extend(persistent_cookie_detection.get_jobs())
        _jobs.extend(fingerprint_match_detection.get_jobs())
        _jobs.extend(db_backup.get_jobs())
        _jobs.extend(close_tournament_registrations.get_jobs())
    return _jobs