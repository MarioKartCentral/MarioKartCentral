from datetime import timedelta
from dataclasses import dataclass
import json
from typing import Any

from worker.data import handle
from worker.jobs import Job
from common.data.commands import Command

@dataclass
class FingerprintMatchDetectionState:
    last_login_id: int = -1

@dataclass
class DetectFingerprintMatchesCommand(Command[FingerprintMatchDetectionState]):
    state: FingerprintMatchDetectionState

    async def handle(self, db_wrapper, s3_wrapper) -> FingerprintMatchDetectionState:
        async with db_wrapper.connect(db_name='user_activity', readonly=True) as db:
            get_max_query = """
                SELECT MAX(id) FROM user_logins
            """
            async with db.execute(get_max_query) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] is None:
                    return self.state
                
                max_login_id = row[0]

        if max_login_id == self.state.last_login_id:
            return self.state
        
        new_state = FingerprintMatchDetectionState(last_login_id=max_login_id)
        
        async with db_wrapper.connect(db_name='alt_flags', attach=["user_activity"]) as db:
            potential_matches_query = """
                SELECT l1.user_id AS user_id_1, l2.user_id AS user_id_2, l1.fingerprint, MIN(l1.date) AS date_1, MIN(l2.date) AS date_2, MIN(l1.id) AS login_id_1, MIN(l2.id) AS login_id_2
                FROM user_activity.user_logins l1
                JOIN user_activity.user_logins l2 ON 
                    l1.fingerprint = l2.fingerprint AND
                    l1.user_id < l2.user_id -- Ensures each pair is only counted once
                WHERE
                    (l1.id > :last_login_id OR l2.id > :last_login_id) AND 
                    NOT EXISTS (SELECT 1 FROM alt_flags WHERE type = 'fingerprint_match' AND flag_key = 'user_id_1=' || l1.user_id || ',user_id_2=' || l2.user_id)
                GROUP BY l1.user_id, l2.user_id, l1.fingerprint
            """
            
            potential_matches = await db.execute_fetchall(potential_matches_query, {
                "last_login_id": self.state.last_login_id
            })
            
            if not potential_matches:
                return new_state
            
            new_flags: list[dict[str, Any]] = []
            for user_id_1, user_id_2, fingerprint, date_1, date_2, login_id_1, login_id_2 in potential_matches:
                if date_1 > date_2:
                    date = date_1
                    login_id = login_id_1
                else:
                    date = date_2
                    login_id = login_id_2

                alt_flag_data: dict[str, Any] = {
                    "type": "fingerprint_match",
                    "flag_key": f"user_id_1={user_id_1},user_id_2={user_id_2}",
                    "data": json.dumps({
                        "user_id_1": user_id_1, 
                        "user_id_2": user_id_2, 
                        "fingerprint": fingerprint, 
                        "date_1": date_1,
                        "date_2": date_2,
                        "login_id_1": login_id_1, 
                        "login_id_2": login_id_2
                    }),
                    "score": 15,
                    "date": date,
                    "login_id": login_id
                }
                new_flags.append(alt_flag_data)

            # Get the id of the most recent alt flag
            get_max_flag_id_query = """
                SELECT MAX(id) FROM alt_flags
            """
            async with db.execute(get_max_flag_id_query) as cursor:
                row = await cursor.fetchone()
                prev_max_flag_id = -1 if not row or row[0] is None else row[0]
            
            insert_flags_query = """
                INSERT INTO alt_flags(type, flag_key, data, score, date, login_id)
                VALUES (:type, :flag_key, :data, :score, :date, :login_id)
                ON CONFLICT (type, flag_key) DO NOTHING
            """
            await db.executemany(insert_flags_query, new_flags)

            # Now we need to insert the user_alt_flags entries
            insert_user_alt_flags_query = """
                WITH new_flags AS (
                    SELECT id, json_extract(data, '$.user_id_1') AS user_id_1, json_extract(data, '$.user_id_2') AS user_id_2
                    FROM alt_flags
                    WHERE type = 'fingerprint_match' AND id > :prev_max_flag_id
                ),
                new_user_flags AS (
                    SELECT user_id_1 AS user_id, id FROM new_flags
                    UNION ALL
                    SELECT user_id_2 AS user_id, id FROM new_flags
                )
                INSERT INTO user_alt_flags(user_id, flag_id)
                SELECT user_id, id FROM new_user_flags
            """

            await db.execute(insert_user_alt_flags_query, {"prev_max_flag_id": prev_max_flag_id})
            await db.commit()
            
        return new_state

class FingerprintMatchDetectionJob(Job):
    @property
    def name(self):
        return "Detect Users with matching fingerprints"
    
    @property
    def delay(self):
        return timedelta(minutes=5)  # Run every 5 minutes
    
    async def run(self):
        # Get the previous state
        state = await self.get_state(FingerprintMatchDetectionState)
        if not state:
            state = FingerprintMatchDetectionState()
            
        # Run the command with the state object
        new_state = await handle(DetectFingerprintMatchesCommand(state=state))
        
        # Update the state
        await self.update_state(new_state)

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(FingerprintMatchDetectionJob())
    return _jobs
