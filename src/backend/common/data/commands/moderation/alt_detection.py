from dataclasses import dataclass
from typing import Dict, Any
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
class GetFingerprintDataCommand(Command[Fingerprint]):
    fingerprint_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        fingerprint_bytes = await s3_wrapper.get_object(s3.FINGERPRINT_BUCKET, f"{self.fingerprint_hash}.json")
        if not fingerprint_bytes:
            raise Problem("Fingerprint not found", status=404)
        fingerprint_data = msgspec.json.decode(fingerprint_bytes, type=dict[Any, Any])
        fingerprint = Fingerprint(self.fingerprint_hash, fingerprint_data)
        return fingerprint

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
            url = "http://ip-api.com/batch?fields=status,message,mobile,proxy,countryCode,region,city,as"
            # we can specify 100 IPs per request, so send requests in chunks of 100
            chunk_size = 100
            for i in range(0, len(ips_to_check), chunk_size):
                data = [ip.ip_address for ip in ips_to_check[i:i+chunk_size]]
                async with session.post(url, json=data) as resp:
                    if int(resp.status/100) != 2:
                        raise Problem("Error when sending request to IP site")
                    r = await resp.json()
                    body = msgspec.convert(r, type=list[IPCheckResponse])
                    # get ASNs since they are named "as" which we cannot put in a class name
                    for i in range(len(r)):
                        body[i].asn = r[i].get("as", None)
                    response_data.extend(body)
        
        # Update the ip_addresses table with the check results
        query_parameters: List[Dict[str, Any]] = [
            {
                "id": ips_to_check[i].user_id,  # This is the ip_address.id
                "is_mobile": response_data[i].mobile, 
                "is_vpn": response_data[i].proxy,
                "country": response_data[i].countryCode,
                "region": response_data[i].region,
                "city": response_data[i].city,
                "asn": response_data[i].asn,
                "checked_at": current_timestamp
            } for i in range(len(ips_to_check))
        ]
        
        async with db_wrapper.connect(db_name='user_activity') as db:
            update_ip_check_results_command = """
                UPDATE ip_addresses 
                SET is_mobile = :is_mobile, is_vpn = :is_vpn, country = :country,
                region = :region, city = :city, asn = :asn,
                is_checked = 1, checked_at = :checked_at
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
            count_query = """SELECT COUNT(*) FROM alt_flags.alt_flags
                    WHERE (:type IS NULL OR type = :type)
                    AND (:exclude_fingerprints=0 OR type != 'fingerprint_match')"""
            async with db.execute(count_query, {"type": self.filter.type,
                                                "exclude_fingerprints": self.filter.exclude_fingerprints}) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = row[0]
            page_count = (count + limit - 1) // limit

            get_flags_query = """
                SELECT f.id, f.type, f.flag_key, f.data, f.score, f.date, l.fingerprint,
                       u.id as user_id, p.id as player_id, p.name as player_name, p.country_code, p.is_banned
                FROM (
                    SELECT id FROM alt_flags.alt_flags
                    WHERE (:type IS NULL OR type = :type)
                    AND (:exclude_fingerprints=0 OR type != 'fingerprint_match')
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
            async with db.execute(get_flags_query, {"limit": limit, "offset": offset, "type": self.filter.type,
                                                    "exclude_fingerprints": self.filter.exclude_fingerprints}) as cursor:
                rows = await cursor.fetchall()
                for flag_id, flag_type, flag_key, data, score, date, fingerprint_hash, user_id, player_id, player_name, player_country, player_banned in rows:
                    # Create flag if we haven't seen it yet
                    if flag_id not in flag_dict:
                        flag_dict[flag_id] = AltFlag(flag_id, flag_type, flag_key, data, score, date, fingerprint_hash, [])
                    
                    # Add player if we have player data (might be NULL if no players associated)
                    if user_id is not None:
                        player = None
                        if player_id is not None:
                            player = PlayerBasic(player_id, player_name, player_country, bool(player_banned))
                        flag_user = AltFlagUser(user_id, player)
                        flag_dict[flag_id].users.append(flag_user)

            return AltFlagList(list(flag_dict.values()), count, page_count)

@dataclass
class ViewPlayerAltFlagsCommand(Command[list[AltFlag]]):
    player_id: int
    exclude_fingerprints: bool

    async def handle(self, db_wrapper, s3_wrapper):
        # get alt flag info
        async with db_wrapper.connect(db_name="main", attach=["user_activity", "alt_flags"], readonly=True) as db:

            get_user_player_info = """
                SELECT u.id as user_id, p.id, p.name, p.country_code, p.is_banned
                FROM main.users u
                JOIN main.players p ON u.player_id = p.id
                WHERE p.id = :player_id
            """
            async with db.execute(get_user_player_info, {"player_id": self.player_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                user_id, player_id, player_name, player_country, player_banned = row
                current_player = PlayerBasic(player_id, player_name, player_country, bool(player_banned))
                current_user = AltFlagUser(user_id, current_player)
                

            flag_dict: dict[int, AltFlag] = {}
            get_player_flags_command = """
                SELECT f.id, f.type, f.flag_key, f.data, f.score, f.date, l.fingerprint 
                FROM alt_flags.alt_flags f
                JOIN alt_flags.user_alt_flags uf ON f.id = uf.flag_id
                LEFT JOIN user_activity.user_logins l ON f.login_id = l.id
                WHERE uf.user_id = :user_id
                AND (:exclude_fingerprints=0 OR f.type != 'fingerprint_match')
                ORDER BY f.date DESC
            """
            async with db.execute(get_player_flags_command, {"user_id": user_id, "exclude_fingerprints": self.exclude_fingerprints}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    flag_id, type, flag_key, data, score, date, fingerprint_hash = row
                    flag = AltFlag(flag_id, type, flag_key, data, score, date, fingerprint_hash, [current_user])
                    flag_dict[flag_id] = flag

           # get other players with the same flags
            get_flag_players_command = """
                SELECT u.id, p.id, p.name, p.country_code, p.is_banned, uf2.flag_id
                FROM alt_flags.user_alt_flags uf1
                JOIN alt_flags.user_alt_flags uf2 ON uf1.flag_id = uf2.flag_id
                JOIN main.users u ON uf2.user_id = u.id
                LEFT JOIN main.players p ON u.player_id = p.id
                WHERE uf1.user_id = :user_id
                AND uf2.user_id != :user_id
            """
            async with db.execute(get_flag_players_command, {"user_id": user_id}) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    user_id, player_id, player_name, player_country, player_banned, flag_id = row
                    flag = flag_dict.get(flag_id)
                    if flag:
                        current_player = None
                        if player_id:
                            current_player = PlayerBasic(player_id, player_name, player_country, bool(player_banned))
                        flag.users.append(AltFlagUser(user_id, current_player))
            
            return list(flag_dict.values())
        
@dataclass
class ViewPlayerLoginHistoryCommand(Command[PlayerUserLogins]):
    player_id: int
    has_ip_permission: bool

    async def handle(self, db_wrapper, s3_wrapper):
        logins: list[UserLogin] = []
        async with db_wrapper.connect(db_name='main', attach=['user_activity']) as db:
            async with db.execute("""SELECT ul.id, ul.user_id, ul.ip_address_id,
                                    ul.fingerprint, ul.had_persistent_session, ul.date,
                                    ul.logout_date, ip.ip_address, ip.is_mobile,
                                    ip.is_vpn, ip.country, ip.region, ip.city, ip.asn
                                    FROM players p
                                    JOIN users u ON u.player_id = p.id
                                    JOIN user_activity.user_logins ul ON u.id = ul.user_id
                                    JOIN user_activity.ip_addresses ip ON ul.ip_address_id = ip.id
                                    WHERE p.id = ? ORDER BY ul.date DESC""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (login_id, user_id, ip_address_id, fingerprint, had_persistent_session, login_date,
                        logout_date, ip_address, is_mobile, is_vpn, ip_country, ip_region,
                        ip_city, ip_asn) = row
                    if not self.has_ip_permission:
                        ip_address = None
                        ip_city = None
                    ip = IPAddress(ip_address_id, ip_address, bool(is_mobile), bool(is_vpn), ip_country, ip_region, ip_city, ip_asn)
                    login = UserLogin(login_id, user_id, fingerprint, bool(had_persistent_session), login_date, logout_date, ip)
                    logins.append(login)
        return PlayerUserLogins(self.player_id, logins)

@dataclass
class ViewPlayerIPHistoryCommand(Command[PlayerIPHistory]):
    player_id: int
    has_ip_permission: bool

    async def handle(self, db_wrapper, s3_wrapper):
        ips: list[UserIPTimeRange] = []
        async with db_wrapper.connect(db_name='main', attach=['user_activity']) as db:
            async with db.execute("""SELECT tr.id, tr.date_earliest, tr.date_latest, tr.times,
                                    uip.user_id, ip.id, ip.ip_address, ip.is_mobile, ip.is_vpn,
                                    ip.country, ip.region, ip.city, ip.asn
                                    FROM players p
                                    JOIN users u ON u.player_id = p.id
                                    JOIN user_activity.user_ips uip ON u.id = uip.user_id
                                    JOIN user_activity.user_ip_time_ranges tr ON uip.id = tr.user_ip_id
                                    JOIN user_activity.ip_addresses ip ON uip.ip_address_id = ip.id
                                    WHERE p.id = ? ORDER BY tr.date_latest DESC""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (time_range_id, date_earliest, date_latest, times, user_id, ip_id, ip_address,
                     is_mobile, is_vpn, country, region, city, asn) = row
                    if not self.has_ip_permission:
                        ip_address = None
                        city = None
                    ip = IPAddress(ip_id, ip_address, bool(is_mobile), bool(is_vpn), country, region, city, asn)
                    time_range = UserIPTimeRange(time_range_id, user_id, ip, date_earliest, date_latest, times)
                    ips.append(time_range)
                ip_history = PlayerIPHistory(self.player_id, ips)
                return ip_history
            
@dataclass
class ViewHistoryForIPCommand(Command[IPHistory]):
    ip_id: int
    has_ip_permission: bool

    async def handle(self, db_wrapper, s3_wrapper):
        time_ranges: list[PlayerIPTimeRange] = []
        async with db_wrapper.connect(db_name='main', attach=['user_activity']) as db:
            async with db.execute("""SELECT ip.id, ip.ip_address, ip.is_mobile, ip.is_vpn,
                                    ip.country, ip.region, ip.city, ip.asn,
                                    uip.user_id, tr.id, tr.date_earliest,
                                    tr.date_latest, tr.times, p.id, p.name, p.country_code, p.is_banned
                                    FROM user_activity.ip_addresses ip
                                    JOIN user_activity.user_ips uip ON ip.id = uip.ip_address_id
                                    JOIN user_activity.user_ip_time_ranges tr ON uip.id = tr.user_ip_id
                                    JOIN users u ON uip.user_id = u.id
                                    LEFT JOIN players p ON u.player_id = p.id
                                    WHERE ip.id = ? ORDER BY tr.date_latest DESC""",
                                    (self.ip_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (ip_id, ip_address, is_mobile, is_vpn, ip_country, ip_region, ip_city, ip_asn,
                        user_id, time_range_id,
                        date_earliest, date_latest, times, player_id, player_name, player_country, player_banned) = row
                    if not self.has_ip_permission:
                        ip_address = None
                        ip_city = None
                    ip = IPAddress(ip_id, ip_address, bool(is_mobile), bool(is_vpn), ip_country, ip_region, ip_city, ip_asn)
                    ip_time_range = UserIPTimeRange(time_range_id, user_id, ip, date_earliest, date_latest, times)
                    player = None
                    if player_id:
                        player = PlayerBasic(player_id, player_name, player_country, bool(player_banned))
                    player_time_range = PlayerIPTimeRange(ip_time_range, player)
                    time_ranges.append(player_time_range)
        ip_history = IPHistory(self.ip_id, time_ranges)
        return ip_history
    
@dataclass
class SearchIPsCommand(Command[IPAddressList]):
    filter: IPFilter
    has_ip_permission: bool

    async def handle(self, db_wrapper, s3_wrapper):
        limit = 20
        offset = 0

        if self.filter.page:
            offset = (self.filter.page - 1) * limit
        ip_filter = f"{self.filter.ip_address}%" if self.has_ip_permission and self.filter.ip_address else None
        city_filter = f"{self.filter.city}%" if self.has_ip_permission and self.filter.city else None
        query_parameters: dict[str, Any] = {
            "ip_address": ip_filter,
            "city": city_filter,
            "asn": f"{self.filter.asn}%" if self.filter.asn else None,
            "offset": offset,
            "limit": limit,
        }
        results: list[IPAddressWithUserCount] = []
        async with db_wrapper.connect(db_name='user_activity') as db:
            query = """FROM ip_addresses ip
                        JOIN user_ips uip ON ip.id = uip.ip_address_id
                        WHERE (:ip_address IS NULL OR ip.ip_address LIKE :ip_address) AND (:city IS NULL OR ip.city LIKE :city)
                        AND (:asn IS NULL OR ip.asn LIKE :asn)
                        GROUP BY ip.id, ip.ip_address, ip.is_mobile, ip.is_vpn, ip.country, ip.city, ip.region
                        """
            async with db.execute(f"""SELECT ip.id, ip.ip_address, ip.is_mobile, ip.is_vpn, ip.country, ip.city, ip.region, ip.asn, COUNT(uip.user_id)
                                    {query} LIMIT :limit OFFSET :offset
                                  """, query_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ip_id, ip_address, is_mobile, is_vpn, country, city, region, asn, user_count = row
                    if not self.has_ip_permission:
                        ip_address = None
                        city = None
                    ip = IPAddressWithUserCount(ip_id, ip_address, is_mobile, is_vpn, country, city, region, asn, user_count)
                    results.append(ip)
            
            count_query = f"SELECT COUNT(*) FROM (SELECT ip.id {query})"
            async with db.execute(count_query, query_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = int(row[0])
            page_count = (count + limit - 1) // limit
            return IPAddressList(results, count, page_count)
    
@dataclass
class GetIPIDFromAddressCommand(Command[int]):
    ip_address: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='user_activity') as db:
            async with db.execute("SELECT id FROM ip_addresses WHERE ip_address = ?", (self.ip_address,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("IP not found", status=404)
                ip_id = row[0]
                return ip_id