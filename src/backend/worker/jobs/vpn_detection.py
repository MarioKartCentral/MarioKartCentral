from datetime import timedelta
from dataclasses import dataclass
import json
from typing import Any

from common.data.command import Command
from common.data.db import DBWrapper
from worker.data import handle
from worker.jobs.base import Job

@dataclass
class VPNDetectionState:
    last_user_ip_id: int = -1
    last_checked_timestamp: int = -1

@dataclass
class DetectVPNUsersCommand(Command[VPNDetectionState]):
    state: VPNDetectionState

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='user_activity', readonly=True) as db:
            get_maxs_query = """
                SELECT
                    (SELECT MAX(id) FROM user_ips) as max_user_ip_id,
                    (SELECT MAX(checked_at) FROM ip_addresses WHERE is_checked = 1) as max_checked_at
            """
            async with db.execute(get_maxs_query) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return self.state
                
                max_user_ip_id = row[0] if row[0] is not None else self.state.last_user_ip_id
                max_checked_at = row[1] if row[1] is not None else self.state.last_checked_timestamp

        if max_user_ip_id == self.state.last_user_ip_id and max_checked_at == self.state.last_checked_timestamp:
            return self.state
        
        new_state = VPNDetectionState(
            last_user_ip_id=max_user_ip_id,
            last_checked_timestamp=max_checked_at
        )
        
        async with db_wrapper.connect(db_name='alt_flags', attach=["user_activity"]) as db:
            get_new_vpn_flags_query = """
                SELECT ui.user_id, MIN(tr.date_earliest) AS date_earliest
                FROM user_activity.user_ips ui
                JOIN user_activity.user_ip_time_ranges tr ON ui.id = tr.user_ip_id
                JOIN user_activity.ip_addresses ip ON ui.ip_address_id = ip.id
                WHERE (ip.checked_at > :last_checked_timestamp OR ui.id > :last_user_ip_id)
                AND ui.id <= :max_user_ip_id
                AND ip.checked_at <= :max_checked_at
                AND ip.is_vpn = 1
                AND ip.is_checked = 1
                AND NOT EXISTS (SELECT 1 FROM alt_flags WHERE type = 'vpn' AND flag_key = CAST(ui.user_id AS TEXT))
                GROUP BY ui.user_id
            """

            new_vpn_flags = await db.execute_fetchall(get_new_vpn_flags_query, {
                "last_checked_timestamp": self.state.last_checked_timestamp,
                "last_user_ip_id": self.state.last_user_ip_id,
                "max_user_ip_id": max_user_ip_id,
                "max_checked_at": max_checked_at
            })

            if not new_vpn_flags:
                return new_state
            
            new_flags: list[dict[str, Any]] = []
            for user_id, date in new_vpn_flags:
                alt_flag_data: dict[str, Any] = {
                    "type": "vpn",
                    "flag_key": user_id,
                    "data": json.dumps({"user_id": user_id}),
                    "score": 1,
                    "date": date,
                }
                new_flags.append(alt_flag_data)

            # Get the current max ID from alt_flags
            get_max_flag_id_query = """
                SELECT MAX(id) FROM alt_flags
            """
            async with db.execute(get_max_flag_id_query) as cursor:
                row = await cursor.fetchone()
                prev_max_flag_id = -1 if not row or row[0] is None else row[0]

            create_alt_flags_query = """
                INSERT INTO alt_flags(type, flag_key, data, score, date, login_id)
                VALUES (:type, :flag_key, :data, :score, :date, NULL)
                ON CONFLICT (type, flag_key) DO NOTHING
            """
            await db.executemany(create_alt_flags_query, new_flags)
            
            # Now we need to insert the user_alt_flags entries
            insert_user_alt_flags_query = """
                WITH new_flags AS (
                    SELECT id, json_extract(data, '$.user_id') AS user_id
                    FROM alt_flags
                    WHERE type = 'vpn' AND id > :prev_max_flag_id
                )
                INSERT INTO user_alt_flags(user_id, flag_id)
                SELECT user_id, id FROM new_flags
            """
            
            await db.execute(insert_user_alt_flags_query, {"prev_max_flag_id": prev_max_flag_id})
            await db.commit()

        return new_state


class VPNDetectionJob(Job):
    @property
    def name(self):
        return "Detect Users with VPN connections"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        # Get the previous state
        state = await self.get_state(VPNDetectionState)
        if not state:
            state = VPNDetectionState()
            
        # Run the command with the state object
        new_state = await handle(DetectVPNUsersCommand(state=state))
        
        # Update the state
        await self.update_state(new_state)

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(VPNDetectionJob())
    return _jobs
