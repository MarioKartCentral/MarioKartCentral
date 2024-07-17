from dataclasses import dataclass
from typing import Callable, Literal

from aiosqlite import Connection

from common.data.commands import Command, save_to_command_log
from common.data.models import *

async def player_exists_in_table(db: Connection, table: Literal['players', 'player_bans'], player_id: int) -> bool:
    """ Check if a player is in either the players or player_bans db table """
    if table == 'players':
        command = "SELECT EXISTS (SELECT 1 FROM players WHERE id = ?)"
    else:
        command = "SELECT EXISTS (SELECT 1 FROM player_bans WHERE player_id = ?)"

    async with db.execute(command, (player_id, )) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        return True if row[0] else False

@save_to_command_log
@dataclass
class BanPlayerCommand(Command[PlayerBan]):
    player_id: int
    staff_id: int
    data: PlayerBanRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data

        async with db_wrapper.connect() as db:
            command = "INSERT INTO player_bans(player_id, staff_id, is_indefinite, expiration_date, reason) VALUES (?, ?, ?, ?, ?)"
            params = (self.player_id, self.staff_id, data.is_indefinite, data.expiration_date, data.reason)
            
            try:
                player_row = await db.execute_insert(command, params)
                if player_row is None:
                    raise Problem("Failed to ban player", "Failed to insert into ban table")
            except Exception as e:
                if not await player_exists_in_table(db, 'players', self.player_id):
                    raise Problem("Player not found", status=404)
                if await player_exists_in_table(db, 'player_bans', self.player_id):
                    raise Problem("Player is already banned", status=400)
                raise Problem("Error", detail=str(e))

            async with db.execute("""UPDATE players SET is_banned = TRUE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to ban player", "Failed to update is_banned in player table")
            
            await db.commit()
            return PlayerBan(*params)

@save_to_command_log
@dataclass
class UnbanPlayerCommand(Command[None]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("DELETE FROM player_bans WHERE player_id = ?", (self.player_id, )) as cursor:
                rowcount = cursor.rowcount

            if rowcount != 1:
                raise Problem("Player not found", "Unable to find player in the ban table", status=404)
            
            async with db.execute("""UPDATE players SET is_banned = FALSE WHERE id = ?""", (self.player_id,)) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to unban player", "Failed to update is_banned in player table")
            await db.commit()

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

            await db.commit()
            return PlayerBan(self.player_id, self.staff_id, data.is_indefinite, data.expiration_date, data.reason)

@dataclass
class ListBannedPlayersCommand(Command[list[PlayerBan]]):
    filter: PlayerBanFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter

        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

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
            append_equal_filter(filter.reason, 'reason', "reason LIKE ?", var_param=f"%{filter.reason}%")

            where_clause = "" if not where_clauses else f"WHERE {' AND '.join(where_clauses)}"
            query = f"""SELECT player_id, staff_id, is_indefinite, expiration_date, reason from player_bans {where_clause}"""

            player_bans: list[PlayerBan] = []
            async with db.execute(query, variable_parameters) as cursor:
                while True:
                    batch = await cursor.fetchmany(50)
                    if not batch:
                        break

                    for row in batch:
                        player_bans.append(PlayerBan(*row))
            
            return player_bans