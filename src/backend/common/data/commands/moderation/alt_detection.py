from dataclasses import dataclass
from typing import Dict
from common.data.commands import Command
from common.data.models import *
import msgspec
import common.data.s3 as s3
from datetime import datetime
import aiohttp

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
        ips_to_check: list[IPInfoBasic] = []
        
        # Get unchecked IP addresses
        async with db_wrapper.connect(db_name='user_activity', readonly=True) as db:
            get_unchecked_ips_command = "SELECT id, ip_address FROM ip_addresses WHERE is_checked = 0 LIMIT :limit"
            async with db.execute(get_unchecked_ips_command, {"limit": limit}) as cursor:
                rows = await cursor.fetchall()
                # We don't need user_id for checking IPs anymore, just using a dummy value
                for row in rows:
                    ip_id, ip_address = row
                    # Map ip_id to user_id when creating IPInfoBasic
                    ips_to_check.append(IPInfoBasic(user_id=ip_id, ip_address=ip_address))
                    
        if len(ips_to_check) == 0:
            return
            
        response_data: list[IPCheckResponse] = []
        current_timestamp = int(datetime.now().timestamp())
        async with aiohttp.ClientSession() as session:
            url = "http://ip-api.com/batch?fields=status,message,mobile,proxy"
            # we can specify 100 IPs per request, so send requests in chunks of 100
            chunk_size = 100
            for i in range(0, len(ips_to_check), chunk_size):
                data = [ip.ip_address for ip in ips_to_check[i:i+chunk_size]]
                async with session.post(url, json=data) as resp:
                    if int(resp.status/100) != 2:
                        raise Problem("Error when sending request to IP site")
                    r = await resp.json()
                    body = msgspec.convert(r, type=list[IPCheckResponse])
                    response_data.extend(body)
        
        # Update the ip_addresses table with the check results
        query_parameters: List[Dict[str, Any]] = [
            {
                "id": ips_to_check[i].user_id,  # This is the ip_address.id
                "is_mobile": response_data[i].mobile, 
                "is_vpn": response_data[i].proxy,
                "checked_at": current_timestamp
            } for i in range(len(ips_to_check))
        ]
        
        async with db_wrapper.connect(db_name='user_activity') as db:
            update_ip_check_results_command = """
                UPDATE ip_addresses 
                SET is_mobile = :is_mobile, is_vpn = :is_vpn, is_checked = 1, checked_at = :checked_at
                WHERE id = :id
            """
            await db.executemany(update_ip_check_results_command, query_parameters)
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

            # Get count for pagination
            count_query = "SELECT COUNT(*) FROM alt_flags.alt_flags"
            async with db.execute(count_query) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = row[0]
            page_count = (count + limit - 1) // limit

            get_flags_query = """
                SELECT f.id, f.type, f.flag_key, f.data, f.score, f.date, l.fingerprint,
                       p.id as player_id, p.name as player_name, p.country_code
                FROM (
                    SELECT id FROM alt_flags.alt_flags 
                    ORDER BY date DESC 
                    LIMIT :limit OFFSET :offset
                ) as pf
                JOIN alt_flags.alt_flags f ON f.id = pf.id
                LEFT JOIN user_activity.user_logins l ON f.login_id = l.id
                LEFT JOIN alt_flags.user_alt_flags uf ON f.id = uf.flag_id
                LEFT JOIN main.users u ON uf.user_id = u.id
                LEFT JOIN main.players p ON u.player_id = p.id
                ORDER BY f.date DESC
            """
            
            flag_dict: dict[int, AltFlag] = {}
            async with db.execute(get_flags_query, {"limit": limit, "offset": offset}) as cursor:
                rows = await cursor.fetchall()
                for flag_id, flag_type, flag_key, data, score, date, fingerprint_hash, player_id, player_name, player_country in rows:
                    # Create flag if we haven't seen it yet
                    if flag_id not in flag_dict:
                        flag_dict[flag_id] = AltFlag(flag_id, flag_type, flag_key, data, score, date, fingerprint_hash, [])
                    
                    # Add player if we have player data (might be NULL if no players associated)
                    if player_id is not None:
                        flag_dict[flag_id].players.append(PlayerBasic(player_id, player_name, player_country))

            return AltFlagList(list(flag_dict.values()), count, page_count)

@dataclass
class ViewPlayerAltFlagsCommand(Command[list[AltFlag]]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        # get alt flag info
        async with db_wrapper.connect(db_name="main", attach=["user_activity", "alt_flags"], readonly=True) as db:

            get_user_player_info = """
                SELECT u.id as user_id, p.id, p.name, p.country_code
                FROM main.users u
                JOIN main.players p ON u.player_id = p.id
                WHERE p.id = :player_id
            """
            async with db.execute(get_user_player_info, {"player_id": self.player_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found")
                user_id, player_id, player_name, player_country = row
                current_player = PlayerBasic(player_id, player_name, player_country)

            flag_dict: dict[int, AltFlag] = {}
            get_player_flags_command = """
                SELECT f.id, f.type, f.flag_key, f.data, f.score, f.date, l.fingerprint 
                FROM alt_flags.alt_flags f
                JOIN alt_flags.user_alt_flags uf ON f.id = uf.flag_id
                LEFT JOIN user_activity.user_logins l ON f.login_id = l.id
                WHERE uf.user_id = :user_id
            """
            async with db.execute(get_player_flags_command, {"user_id": user_id}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    flag_id, type, flag_key, data, score, date, fingerprint_hash = row
                    flag = AltFlag(flag_id, type, flag_key, data, score, date, fingerprint_hash, [current_player])
                    flag_dict[flag_id] = flag

           # get other players with the same flags
            get_flag_players_command = """
                SELECT p.id, p.name, p.country_code, uf2.flag_id
                FROM alt_flags.user_alt_flags uf1
                JOIN alt_flags.user_alt_flags uf2 ON uf1.flag_id = uf2.flag_id
                JOIN main.users u ON uf2.user_id = u.id
                JOIN main.players p ON u.player_id = p.id
                WHERE uf1.user_id = :user_id
                AND uf2.user_id != :user_id
            """
            async with db.execute(get_flag_players_command, {"user_id": user_id}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, player_country, flag_id = row
                    flag = flag_dict.get(flag_id)
                    if flag:
                        flag.players.append(PlayerBasic(player_id, player_name, player_country))
            
            return list(flag_dict.values())