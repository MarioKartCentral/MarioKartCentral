from datetime import timedelta
from worker.data import handle
from common.data.commands import RefreshDiscordAccessTokensCommand
from worker.jobs import Job
from worker.settings import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET

class RefreshDiscordTokensJob(Job):
    @property
    def name(self):
        return "Refresh Discord tokens that will expire soon"
    
    @property
    def delay(self):
        return timedelta(minutes=5)
    
    async def run(self):
        await handle(RefreshDiscordAccessTokensCommand(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET))

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(RefreshDiscordTokensJob())
    return _jobs