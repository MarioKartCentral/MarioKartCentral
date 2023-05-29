from dataclasses import dataclass
from typing import List

from common.data.commands import Command
from common.data.models import *


@dataclass
class CreatePlayerCommand(Command[Player]):
    user_id: int | None
    data: CreatePlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        async with db_wrapper.connect() as db:
            if self.user_id is not None:
                async with db.execute("SELECT player_id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] is not None:
                        raise Problem("Can only have one player per user", status=400)
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, discord_id) 
                VALUES (?, ?, ?, ?, ?, ?)"""
            player_row = await db.execute_insert(
                command, 
                (data.name, data.country_code, data.is_hidden, data.is_shadow, data.is_banned, data.discord_id))
            
            # TODO: Run queries to determine why it errored
            if player_row is None:
                raise Problem("Failed to create player")
            
            player_id = player_row[0]

            if self.user_id is not None:
                async with db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id)) as cursor:
                    # handle case where user with the given ID doesn't exist
                    if cursor.rowcount != 1:
                        raise Problem("Invalid User ID", status=404)

            await db.commit()
            return Player(int(player_id), data.name, data.country_code, data.is_hidden, data.is_shadow, data.is_banned, data.discord_id)

@dataclass
class UpdatePlayerCommand(Command[bool]):
    data: EditPlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper) -> bool:
        data = self.data
        async with db_wrapper.connect() as db:
            update_query = """UPDATE players 
            SET name = ?, country_code = ?, is_hidden = ?, is_shadow = ?, is_banned = ?, discord_id = ?
            WHERE id = ?"""
            params = (data.name, data.country_code, data.is_hidden, data.is_shadow, data.is_banned, data.discord_id, data.player_id)

            async with db.execute(update_query, params) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True


@dataclass
class GetPlayerDetailedCommand(Command[PlayerDetailed | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            query = "SELECT name, country_code, is_hidden, is_shadow, is_banned, discord_id FROM players WHERE id = ?"
            async with db.execute(query, (self.id,)) as cursor:
                player_row = await cursor.fetchone()
            
            if player_row is None:
                return None
            
            name, country_code, is_hidden, is_shadow, is_banned, discord_id = player_row
            
            fc_query = "SELECT game, fc, is_verified, is_primary FROM friend_codes WHERE player_id = ?"
            friend_code_rows = await db.execute_fetchall(fc_query, (self.id, ))
            friend_codes = [FriendCode(fc, game, self.id, bool(is_verified), bool(is_primary)) for game, fc, is_verified, is_primary in friend_code_rows]

            user_query = "SELECT id FROM users WHERE player_id = ?"
            async with db.execute(user_query, (self.id,)) as cursor:
                user_row = await cursor.fetchone()
            
            user = None if user_row is None else User(int(user_row[0]), self.id)

            return PlayerDetailed(self.id, name, country_code, is_hidden, is_shadow, is_banned, discord_id, friend_codes, user)
        
@dataclass
class ListPlayersCommand(Command[List[Player]]):
    filter: PlayerFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            if filter.name is not None:
                where_clauses.append(f"name LIKE ?")
                variable_parameters.append(f"%{filter.name}%")

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.country, "country_code")
            append_equal_filter(filter.is_hidden, "is_hidden")
            append_equal_filter(filter.is_shadow, "is_shadow")
            append_equal_filter(filter.is_banned, "is_banned")
            append_equal_filter(filter.discord_id, "discord_id")

            if filter.friend_code is not None or filter.game is not None:
                fc_where_clauses = []

                if filter.friend_code is not None:
                    fc_where_clauses.append("fc LIKE ?")
                    variable_parameters.append(f"%{filter.friend_code}%")
                
                if filter.game is not None:
                    fc_where_clauses.append("game = ?")
                    variable_parameters.append(filter.game)

                fc_where_clause = ' AND '.join(fc_where_clauses)
                where_clauses.append(f"id IN (SELECT player_id from friend_codes WHERE {fc_where_clause})")


            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            players_query = f"SELECT id, name, country_code, is_hidden, is_shadow, is_banned, discord_id FROM players{where_clause}"

            players = []
            async with db.execute(players_query, variable_parameters) as cursor:
                while True:
                    batch = await cursor.fetchmany(50)
                    if not batch:
                        break

                    for row in batch:
                        id, name, country_code, is_hidden, is_shadow, is_banned, discord_id = row
                        players.append(Player(id, name, country_code, is_hidden, is_shadow, is_banned, discord_id))
            
            return players
