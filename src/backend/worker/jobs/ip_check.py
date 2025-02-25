from datetime import timedelta
from worker.data import handle
from common.data.commands import CheckIPsCommand
from worker.jobs import Job

class CheckIPDataJob(Job):
    @property
    def name(self):
        return "Check IPs for mobile/VPN that haven't been checked yet"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        await handle(CheckIPsCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(CheckIPDataJob())
    return _jobs