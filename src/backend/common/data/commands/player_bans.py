from dataclasses import dataclass
from typing import Literal, List
from datetime import datetime, timezone

from aiosqlite import Connection

from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class BanPlayerCommand(Command[PlayerBan]):
    player_id: int
    banned_by: int
    data: PlayerBanRequestData

    async def player_exists_in_table(self, db: Connection, table: Literal['players', 'player_bans'], player_id: int) -> bool:
        """ Check if a player is in either the players or player_bans db table """
        if table == 'players':
            command = "SELECT EXISTS (SELECT 1 FROM players WHERE id = ?)"
        else:
            command = "SELECT EXISTS (SELECT 1 FROM player_bans WHERE player_id = ?)"

        async with db.execute(command, (player_id, )) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            return True if row[0] else False

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        ban_date = int(datetime.now(timezone.utc).timestamp())

        async with db_wrapper.connect() as db:
            command = "INSERT INTO player_bans(player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, comment) VALUES (?, ?, ?, ?, ?, ?, ?)"
            params = (self.player_id, self.banned_by, data.is_indefinite, ban_date, data.expiration_date, data.reason, data.comment)
            
            try:
                player_row = await db.execute_insert(command, params)
                if player_row is None:
                    raise Problem("Failed to ban player", "Failed to insert into ban table")
            except Exception as e:
                if not await self.player_exists_in_table(db, 'players', self.player_id):
                    raise Problem("Player not found", status=404)
                if await self.player_exists_in_table(db, 'player_bans', self.player_id):
                    raise Problem("Player is already banned")
                raise Problem("Error", detail=str(e))

            async with db.execute("""UPDATE players SET is_banned = TRUE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to ban player", "Player not found")
            
            await db.commit()
            return PlayerBan(*params)

@save_to_command_log
@dataclass
class UnbanPlayerCommand(Command[PlayerBanHistorical]):
    player_id: int
    unbanned_by: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        unban_date = int(datetime.now(timezone.utc).timestamp())

        async with db_wrapper.connect() as db:
            # copy current ban into historical ban table
            async with db.execute("SELECT player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, comment FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            player_id, banned_by, is_indefinite, ban_date, expiration_date, reason , comment= row
            async with db.execute("INSERT INTO player_bans_historical(player_id, banned_by, unbanned_by, unban_date, is_indefinite, ban_date, expiration_date, reason, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (player_id, banned_by, self.unbanned_by, unban_date, is_indefinite, ban_date, expiration_date, reason, comment)) as cursor:
                rowcount = cursor.rowcount
                if rowcount != 1:
                    raise Problem("Failed to unban player", "Failed to insert into historical ban table")

            # delete from ban table and set is_banned for the player to false
            async with db.execute("DELETE FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                rowcount = cursor.rowcount
                if rowcount != 1:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            
            async with db.execute("""UPDATE players SET is_banned = FALSE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to unban player", "Failed to update is_banned in player table")
            await db.commit()
        return PlayerBanHistorical(player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, comment, self.unbanned_by)

@save_to_command_log
@dataclass
class EditPlayerBanCommand(Command[PlayerBan]):
    player_id: int
    banned_by: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        
        async with db_wrapper.connect() as db:
            command = "UPDATE player_bans SET banned_by = ?, is_indefinite = ?, expiration_date = ?, reason = ? , comment = ? WHERE player_id = ?"
            params = (self.banned_by, data.is_indefinite, data.expiration_date, data.reason, data.comment, self.player_id)
            
            async with db.execute(command, params) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
                
            async with db.execute("SELECT ban_date FROM player_bans WHERE player_id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_date = row[0]

            await db.commit()
            return PlayerBan(self.player_id, self.banned_by, data.is_indefinite, ban_date, data.expiration_date, data.reason, data.comment)

def _append_equal_filter(where_clauses: list[str], variable_parameters: list[Any], filter_value: Any, where_clause: str, var_param: str | None = None):
    if filter_value is not None and filter_value != "":
        where_clauses.append(where_clause)
        if var_param:
            variable_parameters.append(var_param)
        else:
            variable_parameters.append(filter_value)

@dataclass
class ListBannedPlayersCommand(Command[PlayerBanList]):
    filter: PlayerBanFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter

        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []
            limit:int = 50
            offset:int = 0

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            _append_equal_filter(where_clauses, variable_parameters, filter.player_id, 'p.id = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.name, 'p.name LIKE ?', f"%{filter.name}%")
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_by, 'bbp.name LIKE ?', f"%{filter.reason}%")
            _append_equal_filter(where_clauses, variable_parameters, filter.is_indefinite, 'b.is_indefinite = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_before, 'b.expiration_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_after, 'b.expiration_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_before, 'b.ban_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_after, 'b.ban_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.reason, "b.reason LIKE ?", f"%{filter.reason}%")

            if filter.comment and filter.comment.strip():
                _append_equal_filter(where_clauses, variable_parameters, filter.comment, "b.comment LIKE ?", f"%{filter.comment}%")
            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            joined_tables = """player_bans b
                JOIN players p ON b.player_id = p.id
                JOIN users bbu ON b.banned_by = bbu.id
                LEFT JOIN players bbp ON bbu.player_id = bbp.id"""
            # bbu: BannedByUser, bbp: BannedByPlayer
            ban_query = f"""SELECT p.name, p.id, p.country_code, b.is_indefinite, b.ban_date, b.expiration_date, b.reason, b.comment, b.banned_by, bbp.id, bbp.name
                FROM {joined_tables} {where_clause} ORDER BY b.ban_date DESC LIMIT ? OFFSET ?"""

            ban_list: list[PlayerBanDetailed] = []
            async with db.execute(ban_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBanDetailed(*row))
            

            async with db.execute(f"SELECT COUNT (*) FROM {joined_tables} {where_clause}", variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_count = row[0]

            page_count = int(ban_count / limit) + (1 if ban_count % limit else 0)
            return PlayerBanList(ban_list, ban_count, page_count)
        
@dataclass
class ListBannedPlayersHistoricalCommand(Command[PlayerBanList]):
    filter: PlayerBanHistoricalFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter

        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []
            limit:int = 50
            offset:int = 0

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            _append_equal_filter(where_clauses, variable_parameters, filter.player_id, 'p.id = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.name, 'p.name LIKE ?', f"%{filter.name}%")
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_by, 'bbp.name LIKE ?', f"%{filter.banned_by}%")
            _append_equal_filter(where_clauses, variable_parameters, filter.is_indefinite, 'b.is_indefinite = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_before, 'b.expiration_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_after, 'b.expiration_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_before, 'b.ban_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_after, 'b.ban_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.reason, "b.reason LIKE ?", f"%{filter.reason}%")

            if filter.comment and filter.comment.strip():
                _append_equal_filter(where_clauses, variable_parameters, filter.comment, "b.comment LIKE ?", f"%{filter.comment}%")
            if filter.unbanned_by and filter.unbanned_by.lower() in 'system':
                _append_equal_filter(where_clauses, variable_parameters, filter.unbanned_by, '(ubp.name LIKE ? OR ubu.id IS NULL)', f"%{filter.unbanned_by}%")
            else:
                _append_equal_filter(where_clauses, variable_parameters, filter.unbanned_by, 'ubp.name LIKE ?', f"%{filter.unbanned_by}%")
            _append_equal_filter(where_clauses, variable_parameters, filter.unbanned_before, 'b.unban_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.unbanned_after, 'b.unban_date >= ?')

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            joined_tables = """player_bans_historical b
                JOIN players p ON b.player_id = p.id
                JOIN users bbu ON b.banned_by = bbu.id
                LEFT JOIN players bbp ON bbu.player_id = bbp.id
                LEFT JOIN users ubu ON b.unbanned_by = ubu.id
                LEFT JOIN players ubp ON ubu.player_id = ubp.id"""
            # bbu: BannedByUser, bbp: BannedByPlayer
            ban_query = f"""SELECT p.name, p.id, p.country_code, b.is_indefinite, b.ban_date, b.expiration_date, b.reason, b.comment, b.banned_by, bbp.id, bbp.name, b.unban_date, b.unbanned_by, ubp.id, ubp.name
                FROM {joined_tables} {where_clause} ORDER BY b.ban_date DESC LIMIT ? OFFSET ?"""        

            ban_list: list[PlayerBanDetailed] = []
            async with db.execute(ban_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBanDetailed(*row))
            
            async with db.execute(f"""SELECT COUNT(*) FROM {joined_tables} {where_clause}""", variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_count = row[0]

            page_count = int(ban_count / limit) + (1 if ban_count % limit else 0)
            return PlayerBanList(ban_list, ban_count, page_count)

@dataclass
class GetPlayersToUnbanCommand(Command[List[PlayerBanWithUserId]]):
    async def handle(self, db_wrapper, s3_wrapper):
        now = int(datetime.now(timezone.utc).timestamp())

        async with db_wrapper.connect(readonly=True) as db:
            ban_list: list[PlayerBanWithUserId] = []
            query = """SELECT p.player_id, p.banned_by, p.is_indefinite, p.ban_date, p.expiration_date, p.reason, p.comment, u.id FROM player_bans p 
                JOIN users u ON u.player_id = p.player_id
                WHERE is_indefinite = FALSE AND expiration_date < ?"""
            async with db.execute(query, (now,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBanWithUserId(*row))

                return ban_list