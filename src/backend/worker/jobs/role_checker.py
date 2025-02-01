from datetime import timedelta
from worker.data import handle
from common.data.commands import RemoveExpiredRolesCommand
from worker.jobs import Job

class RemoveExpiredRolesJob(Job):
    @property
    def name(self):
        return "Remove Expired Roles"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        await handle(RemoveExpiredRolesCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(RemoveExpiredRolesJob())
    return _jobs