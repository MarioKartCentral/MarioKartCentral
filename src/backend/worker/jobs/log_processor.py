from datetime import timedelta
from typing import List
from common.data.commands import GetCommandLogsCommand, ClearCommandLogUpToIdCommand, GetHistoricalCommandLogIndexCommand
from worker.data import handle
from worker.jobs import Job
from worker.jobs.log_processors import LogProcessor, get_log_processors

class LogProcessorJob(Job):
    def __init__(self, log_processor: LogProcessor):
        self._log_processor = log_processor

    @property
    def name(self):
        return f"Log Processor: {self._log_processor.name}"
    
    @property
    def delay(self):
        return self._log_processor.delay
    
    async def run(self):
        last_update_id = await self._log_processor.get_last_update_id()
        if last_update_id is None:
            historical_log_index = await handle(GetHistoricalCommandLogIndexCommand())
            await self._log_processor.run_from_start(historical_log_index)
            last_update_id = await self._log_processor.get_last_update_id()
            
        unprocessed_logs = await handle(GetCommandLogsCommand(last_update_id))
        await self._log_processor.process_logs(unprocessed_logs)

class ClearCommandLogsJob(Job):
    @property
    def name(self):
        return "Clear Command Logs"

    @property
    def delay(self):
        return timedelta(minutes=30)

    async def run(self):
        min_update_id = None
        for log_processor in get_log_processors():
            last_update_id = await log_processor.get_last_update_id()
            if min_update_id is None:
                min_update_id = last_update_id
            elif last_update_id is not None:
                min_update_id = min(min_update_id, last_update_id)
                
        if min_update_id is not None:
            await handle(ClearCommandLogUpToIdCommand(min_update_id))

_jobs: List[Job] = []

def get_jobs():
    if not _jobs:
        for log_processor in get_log_processors():
            _jobs.append(LogProcessorJob(log_processor))

        _jobs.append(ClearCommandLogsJob())
    return _jobs