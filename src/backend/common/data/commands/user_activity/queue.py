from dataclasses import dataclass
from datetime import datetime
from common.data.command import Command
from urllib.parse import urlparse

from common.data.db import DBWrapper

@dataclass
class EnqueueUserActivityCommand(Command[None]):
    user_id: int
    ip_address: str | None
    path: str
    timestamp: datetime
    referer: str | None = None

    async def handle(self, db_wrapper: DBWrapper):
        # Parse the URL to remove query parameters
        parsed_path = urlparse(self.path).path
        timestamp = int(self.timestamp.timestamp())
        
        ip = self.ip_address if self.ip_address else "0.0.0.0"
        
        async with db_wrapper.connect(db_name='user_activity_queue') as db:
            await db.execute(
                """
                INSERT INTO user_activity_queue(user_id, ip_address, path, timestamp, referer)
                VALUES(:user_id, :ip_address, :path, :timestamp, :referer)
                """,
                {
                    "user_id": self.user_id,
                    "ip_address": ip,
                    "path": parsed_path,
                    "timestamp": timestamp,
                    "referer": self.referer
                }
            )
            await db.commit()

@dataclass
class ProcessUserActivityQueueCommand(Command[None]):
    batch_size: int = 1000

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='user_activity', attach=["user_activity_queue"]) as db:
            get_id_range_command = """
                SELECT MIN(id), MAX(id)
                FROM user_activity_queue.user_activity_queue
                ORDER BY id
            """
            async with db.execute(get_id_range_command) as cursor:
                id_range = await cursor.fetchone()
                if not id_range or id_range[0] is None:
                    return  # No records to process
                
                min_id, max_possible_id = id_range
                max_id = min(min_id + self.batch_size - 1, max_possible_id)
            
            insert_missing_ips_command = """
                INSERT INTO ip_addresses(ip_address, is_mobile, is_vpn, is_checked)
                SELECT DISTINCT ip_address, FALSE, FALSE, FALSE
                FROM user_activity_queue.user_activity_queue
                WHERE id BETWEEN :min_id AND :max_id
                ON CONFLICT(ip_address) DO NOTHING
            """
            await db.execute(insert_missing_ips_command, { "min_id": min_id, "max_id": max_id })
            await db.commit()

            insert_user_ips_command = """
                INSERT INTO user_ips(user_id, ip_address_id)
                SELECT DISTINCT q.user_id, ip.id
                FROM user_activity_queue.user_activity_queue q
                JOIN ip_addresses ip ON q.ip_address = ip.ip_address
                WHERE q.id BETWEEN :min_id AND :max_id
                ON CONFLICT(user_id, ip_address_id) DO NOTHING
            """
            await db.execute(insert_user_ips_command, {"min_id": min_id, "max_id": max_id})

            insert_user_ip_time_ranges_query = """
                INSERT INTO user_ip_time_ranges(user_ip_id, date_earliest, date_latest, times)
                SELECT ui.id, q.timestamp, q.timestamp, 1
                FROM user_activity_queue.user_activity_queue q
                JOIN ip_addresses ip ON q.ip_address = ip.ip_address
                JOIN user_ips ui ON q.user_id = ui.user_id AND ip.id = ui.ip_address_id
                WHERE q.id BETWEEN :min_id AND :max_id
                GROUP BY ui.id
            """
            await db.execute(insert_user_ip_time_ranges_query, {"min_id": min_id, "max_id": max_id})
            
            # Delete processed records
            delete_command = """
                DELETE FROM user_activity_queue.user_activity_queue
                WHERE id BETWEEN :min_id AND :max_id
            """
            await db.execute(delete_command, {"min_id": min_id, "max_id": max_id})
            await db.commit()
