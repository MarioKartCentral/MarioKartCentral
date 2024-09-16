from datetime import timedelta
from common.data.commands import GetPlayersToUnbanCommand, UnbanPlayerCommand
from worker.data import handle
from worker.jobs import Job

class UnbanPlayersCheckerJob(Job):
    @property
    def name(self):
        return f"Unban Players Checker"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        players_to_unban = await handle(GetPlayersToUnbanCommand())
        if players_to_unban:
            for player in players_to_unban:
                await handle(UnbanPlayerCommand(player.player_id))

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(UnbanPlayersCheckerJob())
    return _jobs