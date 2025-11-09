from datetime import timedelta
from worker.data import handle
from common.data.commands import CloseTournamentRegistrationsCommand
from worker.jobs.base import Job

class CloseTournamentRegistrationsJob(Job):
    @property
    def name(self):
        return "Close registrations for tournaments where the registration deadline has passed"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        await handle(CloseTournamentRegistrationsCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(CloseTournamentRegistrationsJob())
    return _jobs