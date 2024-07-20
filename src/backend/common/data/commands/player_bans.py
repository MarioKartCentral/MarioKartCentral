from dataclasses import dataclass
from typing import Callable, Literal
from datetime import datetime, timezone

from aiosqlite import Connection

from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class BanPlayerCommand(Command[PlayerBan]):
    player_id: int
    staff_id: int
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
            command = "INSERT INTO player_bans(player_id, staff_id, is_indefinite, ban_date, expiration_date, reason) VALUES (?, ?, ?, ?, ?, ?)"
            params = (self.player_id, self.staff_id, data.is_indefinite, ban_date, data.expiration_date, data.reason)
            
            try:
                player_row = await db.execute_insert(command, params)
                if player_row is None:
                    raise Problem("Failed to ban player", "Failed to insert into ban table")
            except Exception as e:
                if not await self.player_exists_in_table(db, 'players', self.player_id):
                    raise Problem("Player not found", status=404)
                if await self.player_exists_in_table(db, 'player_bans', self.player_id):
                    raise Problem("Player is already banned", status=400)
                raise Problem("Error", detail=str(e))

            async with db.execute("""UPDATE players SET is_banned = TRUE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to ban player", "Player not found")
            
            await db.commit()
            return PlayerBan(*params)

@save_to_command_log
@dataclass
class UnbanPlayerCommand(Command[PlayerBan]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            # copy current ban into historical ban table
            async with db.execute("SELECT player_id, staff_id, is_indefinite, ban_date, expiration_date, reason FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            player_id, staff_id, is_indefinite, ban_date, expiration_date, reason = row
            async with db.execute("INSERT INTO player_bans_historical(player_id, staff_id, is_indefinite, ban_date, expiration_date, reason) VALUES (?, ?, ?, ?, ?, ?)", (player_id, staff_id, is_indefinite, ban_date, expiration_date, reason)) as cursor:
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
        return PlayerBan(*row)

@save_to_command_log
@dataclass
class EditPlayerBanCommand(Command[PlayerBan]):
    player_id: int
    staff_id: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        
        async with db_wrapper.connect() as db:
            command = "UPDATE player_bans SET staff_id = ?, is_indefinite = ?, expiration_date = ?, reason = ? WHERE player_id = ?"
            params = (self.staff_id, data.is_indefinite, data.expiration_date, data.reason, self.player_id)
            
            async with db.execute(command, params) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Player not found", "Unable to find player in the ban table", status=404)
                
            async with db.execute("SELECT ban_date FROM player_bans WHERE player_id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_date = row[0]

            await db.commit()
            return PlayerBan(self.player_id, self.staff_id, data.is_indefinite, ban_date, data.expiration_date, data.reason)

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
            table_name = "player_bans_historical" if filter.is_historical == "1" else "player_bans"

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            def append_equal_filter(filter_value: Any, clause_name: str, where_clause: str, var_param: str | None = None, cast_fn: Callable[[str], Any] | None = None):
                if filter_value is not None:
                    where_clauses.append(where_clause)
                    if var_param:
                        variable_parameters.append(var_param)
                    else:
                        if cast_fn:
                            try:
                                filter_value = cast_fn(filter_value)
                            except Exception as e:
                                raise Problem(f"Bad {clause_name} query", detail=str(e), status=400)
                        variable_parameters.append(filter_value)

            append_equal_filter(filter.player_id, 'player_id', 'player_id = ?', cast_fn=int)
            append_equal_filter(filter.staff_id, 'staff_id', 'staff_id = ?', cast_fn=int)
            append_equal_filter(filter.is_indefinite, 'is_indefinite', 'is_indefinite = ?')
            append_equal_filter(filter.expires_before, 'expires_before', 'expiration_date <= ?', cast_fn=int)
            append_equal_filter(filter.expires_after, 'expires_after', 'expiration_date >= ?', cast_fn=int)
            append_equal_filter(filter.banned_before, 'banned_before', 'ban_date <= ?', cast_fn=int)
            append_equal_filter(filter.banned_after, 'banned_after', 'ban_date >= ?', cast_fn=int)
            append_equal_filter(filter.reason, 'reason', "reason LIKE ?", var_param=f"%{filter.reason}%")

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            ban_query = f"""SELECT player_id, staff_id, is_indefinite, ban_date, expiration_date, reason FROM {table_name} {where_clause} LIMIT ? OFFSET ?"""

            ban_list: list[PlayerBan] = []
            async with db.execute(ban_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    ban_list.append(PlayerBan(*row))
            
            async with db.execute(f"SELECT COUNT (*) FROM {table_name}") as cursor:
                row = await cursor.fetchone()
                assert row is not None
                ban_count = row[0]

            page_count = int(ban_count / limit) + (1 if ban_count % limit else 0)
            return PlayerBanList(ban_list, ban_count, page_count)