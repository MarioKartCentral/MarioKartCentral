from datetime import timedelta
from common.data.commands import GetRecordCacheLatestUpdateId, PopulateAllRecordCaches, UpdateRecordCaches, GetRecordCacheUpdates
from worker.data import handle
from worker.jobs.log_processors import LogProcessor


class RecordCacheUpdater(LogProcessor):
    @property
    def name(self):
        return "Record Cache Updater"

    @property
    def delay(self):
        return timedelta(minutes=30)
    
    async def get_last_update_id(self):
        return await handle(GetRecordCacheLatestUpdateId())

    async def run_from_start(self, historical_log_index):
        await handle(PopulateAllRecordCaches())

    async def process_logs(self, logs):
        updates = GetRecordCacheUpdates.get_updates_from_log(logs)
        await handle(UpdateRecordCaches(updates))