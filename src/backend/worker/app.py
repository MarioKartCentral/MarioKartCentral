from typing import Any
from common.gamedata import gamedata
import asyncio
from datetime import timedelta, datetime

async def example_job():
    print(gamedata["games"]["mk8d"]["tracks"][1]["name"]["en"])

# list of jobs and how frequently they should run
jobs = [
    ("Example Job", example_job, timedelta(seconds=30))
]

async def main():
    job_tasks: list[asyncio.Task[Any]] = []
    job_last_run: list[datetime] = []
    job_longer_than_delay: list[bool] = []
    for i, (_, job_func, _) in enumerate(jobs):
        job_last_run.append(datetime.utcnow())
        job_tasks.append(asyncio.create_task(job_func()))
        job_longer_than_delay.append(False)

    while True:
        for i, (job_name, job_func, job_delay) in enumerate(jobs):
            time_since_last_run = datetime.utcnow() - job_last_run[i]
            if time_since_last_run >= job_delay:
                if job_tasks[i].done():
                    if job_longer_than_delay[i]:
                        print(f"Job '{job_name}' took {time_since_last_run}, when delay is {job_delay}")
                        job_longer_than_delay[i] = False
                    
                    job_last_run[i] = datetime.utcnow()
                    job_tasks[i] = asyncio.create_task(job_func())
                else:
                    if not job_longer_than_delay[i]:
                        print(f"Job '{job_name}' is still running after delay of {job_delay}")
                        job_longer_than_delay[i] = True
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())