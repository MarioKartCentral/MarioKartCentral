from datetime import timedelta
from worker.data import handle
from common.data.commands import ProcessUserActivityQueueCommand
from worker.jobs import Job

class ProcessUserActivityQueueJob(Job):
    @property
    def name(self):
        return "Process User Activity Queue"
    
    @property
    def delay(self):
        return timedelta(seconds=30)  # Run every 30 seconds
    
    async def run(self):
        await handle(ProcessUserActivityQueueCommand())

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(ProcessUserActivityQueueJob())
    return _jobs
