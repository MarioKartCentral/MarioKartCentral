from dataclasses import dataclass
from typing import Dict
from common.data.commands import Command
from common.data.models import *
import msgspec
import common.data.s3 as s3
from datetime import datetime, timezone
import aiohttp

@dataclass
class LogUserIPCommand(Command[None]):
    user_id: int
    ip_address: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='user_activity') as db:
            now = int(datetime.now(timezone.utc).timestamp())
            ip = self.ip_address if self.ip_address else "0.0.0.0"
            async with db.execute("UPDATE user_ips SET date_latest = :date_latest, times = times + 1 WHERE user_id = :user_id AND ip_address = :ip_address",
                                  {"date_latest": now, "user_id": self.user_id, "ip_address": ip}) as cursor:
                row_count = cursor.rowcount
            if not row_count:
                await db.execute("""INSERT INTO user_ips(user_id, ip_address, date_earliest, date_latest, times, is_mobile, is_vpn, is_checked)
                                    VALUES(:user_id, :ip_address, :date_earliest, :date_latest, :times, :is_mobile, :is_vpn, :is_checked)""", 
                                {"user_id": self.user_id, "ip_address": ip, "date_earliest": now, "date_latest": now, 
                                 "times": 1, "is_mobile": False, "is_vpn": False, "is_checked": False})
            await db.commit()

@dataclass
class LogFingerprintCommand(Command[None]):
    fingerprint: Fingerprint

    async def handle(self, db_wrapper, s3_wrapper):
        fingerprint_bytes = msgspec.json.encode(self.fingerprint.data)
        await s3_wrapper.put_object(s3.FINGERPRINT_BUCKET, f"{self.fingerprint.hash}.json", fingerprint_bytes)

@dataclass
class CheckIPsCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        limit = 2000 # rate limit of 100 ips/request * 45 requests/min, 2000 just to be safe
        ips: list[IPInfoBasic] = []
        async with db_wrapper.connect(db_name='user_activity', readonly=True) as db:
            async with db.execute("SELECT user_id, ip_address FROM user_ips WHERE is_checked = 0 LIMIT :limit", {"limit": limit}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    user_id, ip = row
                    ips.append(IPInfoBasic(user_id, ip))
        if len(ips) == 0:
            return
        response_data: list[IPCheckResponse] = []
        async with aiohttp.ClientSession() as session:
            url = "http://ip-api.com/batch?fields=status,message,mobile,proxy"
            # we can specify 100 IPs per request, so send requests in chunks of 100
            chunk_size = 100
            for i in range(0, len(ips), chunk_size):
                data = [ip.ip_address for ip in ips[i:i+chunk_size]]
                async with session.post(url, json=data) as resp:
                    if int(resp.status/100) != 2:
                        raise Problem("Error when sending request to IP site")
                    r = await resp.json()
                    body = msgspec.convert(r, type=list[IPCheckResponse])
                    response_data.extend(body)
        
        # updating appropriate rows in the database
        query_parameters: List[Dict[str, Any]] = [{"is_mobile": response_data[i].mobile, "is_vpn": response_data[i].proxy, 
                            "user_id": ips[i].user_id, "ip_address": ips[i].ip_address} for i in range(len(ips))]
        async with db_wrapper.connect(db_name='user_activity') as db:
            await db.executemany("UPDATE user_ips SET is_mobile = :is_mobile, is_vpn = :is_vpn, is_checked = 1 WHERE user_id = :user_id AND ip_address = :ip_address",
                                 query_parameters)
            await db.commit()

@dataclass
class ListAltFlagsCommand(Command[AltFlagList]):
    filter: AltFlagFilter

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name="main", attach=["user_activity", "alt_flags"], readonly=True) as db:
            limit = 20
            offset = 0

            if self.filter.page:
                offset = (self.filter.page - 1) * limit

            # get alt flag info
            flag_dict: dict[int, AltFlag] = {}
            flag_query = """FROM alt_flags.alt_flags f
                            LEFT JOIN user_activity.user_logins l ON f.login_id = l.id
                            """
            async with db.execute(f"SELECT f.id, f.type, f.data, f.score, f.date, l.fingerprint {flag_query} ORDER BY f.date DESC LIMIT ? OFFSET ?",
                                  (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    flag_id, type, data, score, date, fingerprint_hash = row
                    flag = AltFlag(flag_id, type, data, score, date, fingerprint_hash, [])
                    flag_dict[flag_id] = flag
            
            # get player info
            async with db.execute(f"""SELECT p.id, p.name, p.country_code, uf.flag_id
                                    FROM alt_flags.user_alt_flags uf
                                    JOIN users u ON uf.user_id = u.id
                                    JOIN players p ON u.player_id = p.id
                                    WHERE uf.flag_id IN (
                                        SELECT f.id {flag_query}
                                        ORDER BY f.date DESC LIMIT ? OFFSET ?
                                    )""", (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, player_country, flag_id = row
                    flag = flag_dict.get(flag_id)
                    if flag:
                        flag.players.append(PlayerBasic(player_id, player_name, player_country))

            count_query = f"SELECT COUNT(*) FROM (SELECT f.id {flag_query})"
            page_count: int = 0
            count: int = 0
            async with db.execute(count_query) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = row[0]
            page_count = int(count / limit) + (1 if count % limit else 0)

            return AltFlagList(list(flag_dict.values()), count, page_count)

@dataclass
class ViewPlayerAltFlagsCommand(Command[list[AltFlag]]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        # get alt flag info
        async with db_wrapper.connect(db_name="main", attach=["user_activity", "alt_flags"]) as db:
            flag_dict: dict[int, AltFlag] = {}
            flag_query = """FROM alt_flags.alt_flags f
                            LEFT JOIN user_activity.user_logins l ON f.login_id = l.id
                            WHERE f.id IN (
                                SELECT uf.flag_id
                                FROM alt_flags.user_alt_flags uf
                                JOIN users u ON uf.user_id = u.id
                                JOIN players p ON u.player_id = p.id
                                WHERE p.id = ?
                            )"""
            async with db.execute(f"SELECT f.id, f.type, f.data, f.score, f.date, l.fingerprint {flag_query} ORDER BY f.date DESC", 
                                  (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    flag_id, type, data, score, date, fingerprint_hash = row
                    flag = AltFlag(flag_id, type, data, score, date, fingerprint_hash, [])
                    flag_dict[flag_id] = flag

            # get player info
            async with db.execute(f"""SELECT p.id, p.name, p.country_code, uf.flag_id
                                    FROM alt_flags.user_alt_flags uf
                                    JOIN users u ON uf.user_id = u.id
                                    JOIN players p ON u.player_id = p.id
                                    WHERE uf.flag_id IN (
                                        SELECT f.id {flag_query}
                                        ORDER BY f.date
                                    )""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, player_country, flag_id = row
                    flag = flag_dict.get(flag_id)
                    if flag:
                        flag.players.append(PlayerBasic(player_id, player_name, player_country))
            return list(flag_dict.values())