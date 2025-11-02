import asyncio
from datetime import datetime, timezone
import logging
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
        self._tracer = trace.get_tracer("worker.jobs")

    def start(self):
        async def run_with_error_handler():
            with self._tracer.start_as_current_span(
                f"job.run: {self._job.name}",
                attributes={
                    "job.name": self._job.name,
                    "job.delay_seconds": self._job.delay.total_seconds(),
                }
            ):
                try:
                    await self._job.run()
                except Exception:
                    logging.error(
                        f"Job '{self._job.name}' failed",
                        exc_info=True,
                        extra={"job_name": self._job.name}
                    )
                    raise
        
        self._longer_than_delay = False
        self._last_run = datetime.now(timezone.utc)
        self._task = asyncio.create_task(run_with_error_handler())

    def tick(self):
        if self._last_run is None or self._task is None:
            self.start()
            return
        
        time_since_last_run = datetime.now(timezone.utc) - self._last_run
        if time_since_last_run >= self._job.delay:
            if self._task.done():
                if self._longer_than_delay:
                    logging.warning(
                        f"Job '{self._job.name}' took {time_since_last_run} (delay: {self._job.delay})",
                        extra={
                            "job_name": self._job.name,
                            "duration_seconds": time_since_last_run.total_seconds(),
                            "delay_seconds": self._job.delay.total_seconds(),
                        }
                    )

                self.start()
            else:
                if not self._longer_than_delay:
                    logging.warning(
                        f"Job '{self._job.name}' still running after {time_since_last_run} (delay: {self._job.delay})",
                        extra={
                            "job_name": self._job.name,
                            "duration_seconds": time_since_last_run.total_seconds(),
                            "delay_seconds": self._job.delay.total_seconds(),
                        }
                    )
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
        import debugpy # pyright: ignore[reportMissingTypeStubs]
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()  # blocks execution until client is attached

    setup_telemetry()
    asyncio.run(main())