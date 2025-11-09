from datetime import timedelta
from common.data.commands import CompressUserActivityTimeRangesCommand
from worker.data import handle
from worker.jobs.base import Job

class CompressUserActivityTimeRangesJob(Job):
    @property
    def name(self):
        return "Compress User Activity Time Ranges"
    
    @property
    def delay(self):
        return timedelta(minutes=15)  # Run every 15 minutes
    
    async def run(self):
        await handle(CompressUserActivityTimeRangesCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(CompressUserActivityTimeRangesJob())
    return _jobs
