from datetime import timedelta
from typing import Any
from common.data.commands import GetHistoricalCommandLogLastIdCommand, SaveToHistoricalCommandLogsCommand
from common.data.commands import Command
from common.data.models.command_log import CommandLog, HistoricalCommandLogIndexEntry
from worker.data import handle
from worker.jobs.log_processors import LogProcessor


class HistoricalLogBackupLogProcessor(LogProcessor):
    @property
    def name(self):
        return "Historical Command Log Backup"

    @property
    def delay(self):
        return timedelta(minutes=30)

    async def get_last_update_id(self):
        return await handle(GetHistoricalCommandLogLastIdCommand())

    async def run_from_start(self, historical_log_index: list[HistoricalCommandLogIndexEntry]):
        # Since this job is the one that populates the historical log, there is nothing to do when running from start
        return

    async def process_logs(self, logs: list[CommandLog[Command[Any]]]):
        await handle(SaveToHistoricalCommandLogsCommand(logs))