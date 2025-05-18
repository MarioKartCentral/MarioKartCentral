import asyncio
from datetime import datetime, timedelta, timezone
import logging
import time
from common.telemetry import setup_telemetry
from opentelemetry import trace
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
                start = time.time()
                logging.info(f"Job '{self._job.name}' started")
                await self._job.run()
                end = time.time()
                elapsed = timedelta(seconds=end - start)
                logging.info(f"Job '{self._job.name}' completed in {elapsed}")
            except Exception:
                logging.error(f"Job '{self._job.name}' failed", exc_info=True)
        self._longer_than_delay = False
        self._last_run = datetime.now(timezone.utc)
        self._task = asyncio.create_task(run_with_error_handler())

    def tick(self):
        trace.get_current_span().set_attribute("job_name", self._job.name)
        if self._last_run is None or self._task is None:
            self.start()
            return
        
        time_since_last_run = datetime.now(timezone.utc) - self._last_run
        if time_since_last_run >= self._job.delay:
            if self._task.done():
                if self._longer_than_delay:
                    logging.info(f"Job '{self._job.name}' took {time_since_last_run}, when delay is {self._job.delay}")

                self.start()
            else:
                if not self._longer_than_delay:
                    logging.info(f"Job '{self._job.name}' is still running after delay of {self._job.delay}")
                    self._longer_than_delay = True


async def main():
    await on_startup()
    jobs = [JobRunner(job) for job in get_all_jobs()]
    tracer = trace.get_tracer("worker")
    while True:
        for job in jobs:
            with tracer.start_as_current_span("job_tick"):
                job.tick()
        await asyncio.sleep(1)


if __name__ == "__main__":
    if settings.DEBUG:
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()  # blocks execution until client is attached

    setup_telemetry()
    asyncio.run(main())