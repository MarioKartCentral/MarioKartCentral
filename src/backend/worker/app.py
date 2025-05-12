import asyncio
from datetime import datetime, timezone
import traceback
from worker.data import on_startup
from worker import settings
from worker.jobs import Job, get_all_jobs

class JobRunner:
    def __init__(self, job: Job):
        self._job = job
        self._longer_than_delay = False
        self._last_run = None
        self._task = None

    def start(self):
        async def run_with_error_handler():
            try:
                await self._job.run()
            except Exception:
                print(f"Job '{self._job.name}' failed")
                traceback.print_exc()
                raise
    
        self._longer_than_delay = False
        self._last_run = datetime.now(timezone.utc)
        self._task = asyncio.create_task(run_with_error_handler())

    def tick(self):
        if self._last_run is None or self._task is None:
            print(f"Job '{self._job.name}' started")
            self.start()
            return
        
        time_since_last_run = datetime.now(timezone.utc) - self._last_run
        if time_since_last_run >= self._job.delay:
            if self._task.done():
                if self._longer_than_delay:
                    print(f"Job '{self._job.name}' took {time_since_last_run}, when delay is {self._job.delay}")

                self.start()
            else:
                if not self._longer_than_delay:
                    print(f"Job '{self._job.name}' is still running after delay of {self._job.delay}")
                    self._longer_than_delay = True


async def main():
    await on_startup()
    jobs = [JobRunner(job) for job in get_all_jobs()]
    while True:
        for job in jobs:
            job.tick()
        await asyncio.sleep(1)


if __name__ == "__main__":
    if settings.DEBUG:
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()  # blocks execution until client is attached

    asyncio.run(main())