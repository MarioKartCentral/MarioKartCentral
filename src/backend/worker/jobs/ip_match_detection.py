from datetime import timedelta
from dataclasses import dataclass
import json
from typing import Any

from common.data.command import Command
from common.data.db import DBWrapper
from worker.data import handle
from worker.jobs.base import Job

@dataclass
class IPMatchDetectionState:
    last_user_ip_id: int = -1
    last_checked_timestamp: int = -1

@dataclass
class DetectIPMatchesCommand(Command[IPMatchDetectionState]):
    state: IPMatchDetectionState

    async def handle(self, db_wrapper: DBWrapper) -> IPMatchDetectionState:
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
        
        new_state = IPMatchDetectionState(
            last_user_ip_id=max_user_ip_id,
            last_checked_timestamp=max_checked_at
        )
        
        async with db_wrapper.connect(db_name='alt_flags', attach=["user_activity"]) as db:
            # Get the max ID before any operations
            get_max_flag_id_query = """
                SELECT MAX(id) FROM alt_flags
            """
            async with db.execute(get_max_flag_id_query) as cursor:
                row = await cursor.fetchone()
                prev_max_flag_id = -1 if not row or row[0] is None else row[0]
            
            # First, identify all potential matches with their scores
            matches_query = """
                WITH ip_matches AS (
                    SELECT
                        ui1.user_id AS user_id_1,
                        ui2.user_id AS user_id_2,
                        ui1.ip_address_id AS ip_address_id,
                        CASE
                            WHEN ip.is_mobile = 1 THEN 1  -- Mobile IPs get lower score
                            WHEN ip.is_vpn = 1 THEN 3     -- VPN IPs get medium score
                            ELSE 10                       -- Regular IPs get highest score
                        END AS score,
                        'user_id_1=' || ui1.user_id || ',user_id_2=' || ui2.user_id AS flag_key,
                        MIN(MAX(tr1.date_earliest, tr2.date_earliest)) AS match_date,
                        tr1.date_earliest AS date_1,
                        tr2.date_earliest AS date_2,
                        ip.is_mobile AS is_mobile,
                        ip.is_vpn AS is_vpn,
                        ip.country AS country,
                        ip.region AS region,
                        ip.asn AS asn
                    FROM user_activity.user_ips ui1
                    JOIN user_activity.user_ips ui2 ON 
                        ui1.ip_address_id = ui2.ip_address_id AND
                        ui1.user_id < ui2.user_id -- Ensures each pair is only counted once
                    JOIN user_activity.ip_addresses ip ON ui1.ip_address_id = ip.id
                    JOIN user_activity.user_ip_time_ranges tr1 ON ui1.id = tr1.user_ip_id
                    JOIN user_activity.user_ip_time_ranges tr2 ON ui2.id = tr2.user_ip_id
                    WHERE
                        (ip.checked_at > :last_checked_timestamp OR ui1.id > :last_user_ip_id OR ui2.id > :last_user_ip_id) AND
                        ui1.id <= :max_user_ip_id AND
                        ui2.id <= :max_user_ip_id AND
                        ip.checked_at <= :max_checked_at AND
                        ip.is_checked = 1
                    GROUP BY ui1.user_id, ui2.user_id
                )
                SELECT im.user_id_1, im.user_id_2, im.ip_address_id, im.score, im.flag_key, im.match_date, im.date_1, im.date_2, im.is_mobile, im.is_vpn, im.country,
                    im.region, im.asn
                FROM ip_matches im
                LEFT JOIN alt_flags af ON im.flag_key = af.flag_key AND af.type = 'ip_match'
                WHERE af.score IS NULL OR im.score > af.score
            """
            
            potential_matches = await db.execute_fetchall(matches_query, {
                "last_checked_timestamp": self.state.last_checked_timestamp,
                "last_user_ip_id": self.state.last_user_ip_id,
                "max_user_ip_id": max_user_ip_id,
                "max_checked_at": max_checked_at
            })
            
            if not potential_matches:
                return new_state
                
            new_flags: list[dict[str, Any]] = []
            for (user_id_1, user_id_2, ip_address_id, score, flag_key, match_date, date_1, date_2, is_mobile, is_vpn, country,
                 region, asn) in potential_matches:
                data: dict[str, Any] = {
                    "type": "ip_match",
                    "flag_key": flag_key,
                    "data": json.dumps({
                        "user_id_1": user_id_1, 
                        "user_id_2": user_id_2, 
                        "ip_address_id": ip_address_id,
                        "date_1": date_1,
                        "date_2": date_2,
                        "is_mobile": bool(is_mobile),
                        "is_vpn": bool(is_vpn),
                        "country": country,
                        "region": region,
                        "asn": asn,
                    }),
                    "score": score,
                    "date": match_date,
                    "login_id": None
                }
                new_flags.append(data)

            get_max_flag_id_query = """
                SELECT MAX(id) FROM alt_flags
            """
            async with db.execute(get_max_flag_id_query) as cursor:
                row = await cursor.fetchone()
                prev_max_flag_id = -1 if not row or row[0] is None else row[0]

            insert_flags_query = """
                INSERT INTO alt_flags(type, flag_key, data, score, date, login_id)
                VALUES (:type, :flag_key, :data, :score, :date, :login_id)
                ON CONFLICT (type, flag_key) DO UPDATE SET
                    score = excluded.score,
                    date = excluded.date,
                    data = excluded.data
                WHERE excluded.score > alt_flags.score
            """
            await db.executemany(insert_flags_query, new_flags)

            # Now we need to insert the user_alt_flags entries
            insert_user_alt_flags_query = """
                WITH new_flags AS (
                    SELECT id, json_extract(data, '$.user_id_1') AS user_id_1, json_extract(data, '$.user_id_2') AS user_id_2
                    FROM alt_flags
                    WHERE type = 'ip_match' AND id > :prev_max_flag_id
                ),
                new_user_flags AS (
                    SELECT user_id_1 AS user_id, id FROM new_flags
                    UNION ALL
                    SELECT user_id_2 AS user_id, id FROM new_flags
                )
                INSERT INTO user_alt_flags(user_id, flag_id)
                SELECT user_id, id FROM new_user_flags WHERE true
                ON CONFLICT(user_id, flag_id) DO NOTHING
            """
            await db.execute(insert_user_alt_flags_query, {"prev_max_flag_id": prev_max_flag_id})
            await db.commit()

        return new_state

class IPMatchDetectionJob(Job):
    @property
    def name(self):
        return "Detect Users with matching IP addresses"
    
    @property
    def delay(self):
        return timedelta(minutes=1)
    
    async def run(self):
        # Get the previous state
        state = await self.get_state(IPMatchDetectionState)
        if not state:
            state = IPMatchDetectionState()
            
        # Run the command with the state object
        new_state = await handle(DetectIPMatchesCommand(state=state))
        
        # Update the state
        await self.update_state(new_state)

_jobs: list[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(IPMatchDetectionJob())
    return _jobs
