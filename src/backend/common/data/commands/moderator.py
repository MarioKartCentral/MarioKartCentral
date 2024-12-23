from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *

@dataclass
class GetSessionMatchesCommand(Command[SessionMatchList]):
    filter: SessionMatchFilter

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            limit = 10
            offset = 0
            if self.filter.page is not None:
                offset = (self.filter.page - 1) * limit
            
            # session_matches: all persistent_sessions which have more than one user associated with them.
            #       also contains the latest login from that session
            session_matches_query = """WITH session_matches AS (
                    SELECT session_id,
                    MAX (date_latest) AS latest_login,
                    COUNT(user_id)
                    FROM persistent_sessions
                    GROUP BY session_id
                    HAVING COUNT(user_id) > 1   
                )"""
            # ranked_matches: lets us rank session_matches by the latest login time, allowing us to do pagination
            # the final query then retrieves all session/user/player data associated with each user that logged in
            #       for each session_id in the ranked_matches query for the current page.
            session_query = f"""
                {session_matches_query},
                ranked_matches AS (
                    SELECT session_id, latest_login,
                    ROW_NUMBER() OVER (ORDER BY latest_login DESC) AS match_rank
                    FROM session_matches
                )
                SELECT ps.session_id, rm.latest_login, ps.user_id, ps.date_earliest, ps.date_latest,
                    p.id, p.name, p.country_code, p.is_banned
                FROM persistent_sessions ps
                JOIN ranked_matches rm ON ps.session_id = rm.session_id
                JOIN users u ON ps.user_id = u.id
                JOIN players p ON u.player_id = p.id
                WHERE rm.match_rank > ? AND rm.match_rank <= ?
                ORDER BY rm.latest_login DESC
                """
            session_dict: dict[str, SessionMatch] = {}
            async with db.execute(session_query, (offset, limit+offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    session_id, latest_login, user_id, date_earliest, date_latest, player_id, player_name, country_code, is_banned = row
                    if session_id not in session_dict:
                        session_dict[session_id] = SessionMatch(latest_login, [])
                    player_info = PlayerBasic(player_id, player_name, country_code)
                    user_info = SessionMatchUser(user_id, date_earliest, date_latest, player_info, bool(is_banned))
                    session_dict[session_id].users.append(user_info)

            # very important we don't provide the actual session id's in the api response
            session_matches = list(session_dict.values())

            count_query = f"""
                {session_matches_query}
                SELECT COUNT(*) FROM session_matches
                """
            async with db.execute(count_query) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                match_count = row[0]

            page_count = int(match_count / limit) + (1 if match_count % limit else 0)
            match_list = SessionMatchList(session_matches, match_count, page_count)
            return match_list

@dataclass
class GetPlayerSessionMatchesCommand(Command[list[SessionMatch]]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # session_matches: all persistent_sessions which have more than one user associated with them.
            #       also contains the latest login from that session
            session_matches_query = """WITH session_matches AS (
                        SELECT session_id,
                        MAX (date_latest) AS latest_login,
                        COUNT(user_id)
                        FROM persistent_sessions
                        GROUP BY session_id
                        HAVING COUNT(user_id) > 1   
                    )"""
            
            query = f"""{session_matches_query}
                    SELECT ps.session_id, sm.latest_login, ps.user_id, ps.date_earliest, ps.date_latest,
                    p.id, p.name, p.country_code, p.is_banned
                    FROM persistent_sessions ps
                    JOIN session_matches sm ON ps.session_id = sm.session_id
                    JOIN users u ON ps.user_id = u.id
                    JOIN players p ON u.player_id = p.id
                    WHERE ps.session_id IN (
                        SELECT ps.session_id FROM persistent_sessions ps
                        JOIN users u ON ps.user_id = u.id
                        JOIN players p ON u.player_id = p.id
                        WHERE p.id = ?
                    )
                    ORDER BY sm.latest_login DESC"""
            session_dict: dict[str, SessionMatch] = {}
            async with db.execute(query, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    session_id, latest_login, user_id, date_earliest, date_latest, player_id, player_name, country_code, is_banned = row
                    if session_id not in session_dict:
                        session_dict[session_id] = SessionMatch(latest_login, [])
                    player_info = PlayerBasic(player_id, player_name, country_code)
                    user_info = SessionMatchUser(user_id, date_earliest, date_latest, player_info, bool(is_banned))
                    session_dict[session_id].users.append(user_info)

            # very important we don't provide the actual session id's in the api response
            session_matches = list(session_dict.values())
            return session_matches

@dataclass
class GetIPMatchesCommand(Command[IPMatchList]):
    filter: IPMatchFilter
    is_privileged: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            limit = 10
            offset = 0
            if self.filter.page is not None:
                offset = (self.filter.page - 1) * limit

            # ip_matches: all ip addresses which have more than one user associated with them.
            #       also contains the latest login from that ip
            ip_matches_query = """WITH ip_matches AS (
                    SELECT ip_address,
                    MAX (date_latest) AS latest_login,
                    COUNT(user_id)
                    FROM user_ips
                    GROUP BY ip_address
                    HAVING COUNT(user_id) > 1   
                )"""
            # ranked_matches: lets us rank ip_matches by the latest login time, allowing us to do pagination
            # the final query then retrieves all ip/user/player data associated with each user that logged in
            #       for each ip_address in the ranked_matches query for the current page.
            ip_query = f"""{ip_matches_query},
                ranked_matches AS (
                    SELECT ip_address, latest_login,
                    ROW_NUMBER() OVER (ORDER BY latest_login DESC) AS match_rank
                    FROM ip_matches
                )
                SELECT ip.ip_address, rm.latest_login, ip.user_id, ip.date_earliest, ip.date_latest, ip.times,
                    p.id, p.name, p.country_code, p.is_banned
                FROM user_ips ip
                JOIN ranked_matches rm ON ip.ip_address = rm.ip_address
                JOIN users u ON ip.user_id = u.id
                JOIN players p ON u.player_id = p.id
                WHERE rm.match_rank > ? AND rm.match_rank <= ?
                ORDER BY rm.latest_login DESC
                """
            ip_dict: dict[str, IPMatch] = {}
            async with db.execute(ip_query, (offset, limit+offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ip_address, latest_login, user_id, date_earliest, date_latest, times, player_id, player_name, country_code, is_banned = row
                    if ip_address not in ip_dict:
                        # if we don't have privileges to see IP addresses, we should only show the matches but not which IP they came from
                        ip_dict[ip_address] = IPMatch(ip_address if self.is_privileged else None, latest_login, [])
                    player_info = PlayerBasic(player_id, player_name, country_code)
                    user_info = IPMatchUser(user_id, date_earliest, date_latest, times, player_info, bool(is_banned))
                    ip_dict[ip_address].users.append(user_info)

            ip_matches = list(ip_dict.values())

            count_query = f"""
                {ip_matches_query}
                SELECT COUNT(*) FROM ip_matches
                """
            async with db.execute(count_query) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                match_count = row[0]

            page_count = int(match_count / limit) + (1 if match_count % limit else 0)
            match_list = IPMatchList(ip_matches, match_count, page_count)
            return match_list
        
@dataclass
class GetPlayerIPMatchesCommand(Command[list[IPMatch]]):
    player_id: int
    is_privileged: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # ip_matches: all ip addresses which have more than one user associated with them.
            #       also contains the latest login from that ip
            ip_matches_query = """WITH ip_matches AS (
                    SELECT ip_address,
                    MAX (date_latest) AS latest_login,
                    COUNT(user_id)
                    FROM user_ips
                    GROUP BY ip_address
                    HAVING COUNT(user_id) > 1   
                )"""
            query = f"""{ip_matches_query}
                SELECT ip.ip_address, im.latest_login, ip.user_id, ip.date_earliest, ip.date_latest, ip.times,
                    p.id, p.name, p.country_code, p.is_banned
                FROM user_ips ip
                JOIN ip_matches im ON ip.ip_address = im.ip_address
                JOIN users u ON ip.user_id = u.id
                JOIN players p ON u.player_id = p.id
                WHERE ip.ip_address IN (
                    SELECT ip.ip_address
                    FROM user_ips ip
                    JOIN users u ON ip.user_id = u.id
                    JOIN players p ON u.player_id = p.id
                    WHERE p.id = ?
                )
                ORDER BY im.latest_login DESC
                """
            ip_dict: dict[str, IPMatch] = {}
            async with db.execute(query, (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ip_address, latest_login, user_id, date_earliest, date_latest, times, player_id, player_name, country_code, is_banned = row
                    if ip_address not in ip_dict:
                        # if we don't have privileges to see IP addresses, we should only show the matches but not which IP they came from
                        ip_dict[ip_address] = IPMatch(ip_address if self.is_privileged else None, latest_login, [])
                    player_info = PlayerBasic(player_id, player_name, country_code)
                    user_info = IPMatchUser(user_id, date_earliest, date_latest, times, player_info, bool(is_banned))
                    ip_dict[ip_address].users.append(user_info)

            ip_matches = list(ip_dict.values())
            return ip_matches