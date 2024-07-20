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
            command = "INSERT INTO player_bans(player_id, banned_by, is_indefinite, ban_date, expiration_date, reason) VALUES (?, ?, ?, ?, ?, ?)"
            params = (self.player_id, self.banned_by, data.is_indefinite, ban_date, data.expiration_date, data.reason)
            
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
        async with db_wrapper.connect() as db:
            # copy current ban into historical ban table
            async with db.execute("SELECT player_id, banned_by, is_indefinite, ban_date, expiration_date, reason FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            player_id, banned_by, is_indefinite, ban_date, expiration_date, reason = row
            async with db.execute("INSERT INTO player_bans_historical(player_id, banned_by, unbanned_by, is_indefinite, ban_date, expiration_date, reason) VALUES (?, ?, ?, ?, ?, ?, ?)", (player_id, banned_by, self.unbanned_by, is_indefinite, ban_date, expiration_date, reason)) as cursor:
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
        return PlayerBanHistorical(player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, self.unbanned_by)

@save_to_command_log
@dataclass
class EditPlayerBanCommand(Command[PlayerBan]):
    player_id: int
    banned_by: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        
        async with db_wrapper.connect() as db:
            command = "UPDATE player_bans SET banned_by = ?, is_indefinite = ?, expiration_date = ?, reason = ? WHERE player_id = ?"
            params = (self.banned_by, data.is_indefinite, data.expiration_date, data.reason, self.player_id)
            
            async with db.execute(command, params) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
                
            async with db.execute("SELECT ban_date FROM player_bans WHERE player_id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_date = row[0]

            await db.commit()
            return PlayerBan(self.player_id, self.banned_by, data.is_indefinite, ban_date, data.expiration_date, data.reason)

def _append_equal_filter(where_clauses: list[str], variable_parameters: list[Any], filter_value: Any, where_clause: str, var_param: str | None = None):
    if filter_value is not None:
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

            _append_equal_filter(where_clauses, variable_parameters, filter.player_id, 'player_id = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_by, 'banned_by = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.is_indefinite, 'is_indefinite = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_before, 'expiration_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_after, 'expiration_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_before, 'ban_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_after, 'ban_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.reason, "reason LIKE ?", f"%{filter.reason}%")

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            ban_query = f"""SELECT player_id, banned_by, is_indefinite, ban_date, expiration_date, reason FROM player_bans {where_clause} LIMIT ? OFFSET ?"""

            ban_list: list[PlayerBan] = []
            async with db.execute(ban_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBan(*row))
            
            async with db.execute(f"SELECT COUNT (*) FROM player_bans {where_clause}", variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_count = row[0]

            page_count = int(ban_count / limit) + (1 if ban_count % limit else 0)
            return PlayerBanList(ban_list, ban_count, page_count)
        
@dataclass
class ListBannedPlayersHistoricalCommand(Command[PlayerBanHistoricalList]):
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

            _append_equal_filter(where_clauses, variable_parameters, filter.player_id, 'player_id = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_by, 'banned_by = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.unbanned_by, 'unbanned_by = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.is_indefinite, 'is_indefinite = ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_before, 'expiration_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.expires_after, 'expiration_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_before, 'ban_date <= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.banned_after, 'ban_date >= ?')
            _append_equal_filter(where_clauses, variable_parameters, filter.reason, "reason LIKE ?", f"%{filter.reason}%")

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            ban_query = f"""SELECT player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, unbanned_by FROM player_bans_historical {where_clause} LIMIT ? OFFSET ?"""

            ban_list: list[PlayerBanHistorical] = []
            async with db.execute(ban_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBanHistorical(*row))
            
            async with db.execute(f"SELECT COUNT (*) FROM player_bans_historical {where_clause}", variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_count = row[0]

            page_count = int(ban_count / limit) + (1 if ban_count % limit else 0)
            return PlayerBanHistoricalList(ban_list, ban_count, page_count)

@dataclass
class GetPlayersToUnbanCommand(Command[List[PlayerBan]]):
    async def handle(self, db_wrapper, s3_wrapper):
        now = int(datetime.now(timezone.utc).timestamp())

        async with db_wrapper.connect(readonly=True) as db:
            ban_list: list[PlayerBan] = []
            async with db.execute("SELECT player_id, banned_by, is_indefinite, ban_date, expiration_date, reason FROM player_bans WHERE is_indefinite = FALSE AND expiration_date < ?", (now,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBan(*row))

                return ban_list