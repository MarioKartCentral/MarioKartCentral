from datetime import timedelta
from worker.data import handle
from worker.jobs import Job
from common.data.commands import RemoveExpiredTokensCommand

class RemoveExpiredTokensJob(Job):
    @property
    def name(self):
        return "Remove expired email confirmation/password reset tokens"
    
    @property
    def delay(self):
        return timedelta(minutes=5)
    
    async def run(self):
        await handle(RemoveExpiredTokensCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(RemoveExpiredTokensJob())
    return _jobs