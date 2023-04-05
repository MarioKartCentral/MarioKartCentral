from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar
import aiobotocore.session
from common.auth import roles, permissions
import common.data.db.tables as tables
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper
from common.data.models import *


TCommandResponse = TypeVar('TCommandResponse', covariant=True)

# TODO: Split up this file into multiple files that handle specific areas (e.g. tournaments)

class Command(ABC, Generic[TCommandResponse]):
    @abstractmethod
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> TCommandResponse:
        pass

class ResetDbCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        db_wrapper.reset_db()

class InitializeDbSchemaCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("pragma journal_mode = WAL;")
            await db.execute("pragma synchronous = NORMAL;")
            for table in tables.all_tables:
                await db.execute(table.get_create_table_command())

@dataclass
class SeedDatabaseCommand(Command[None]):
    admin_email: str
    hashed_pw: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.executemany(
                "INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_roles_by_id.items())
            
            await db.executemany(
                "INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_role_permission_ids)
            
            await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?)  ON CONFLICT DO NOTHING", (self.admin_email, self.hashed_pw))
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

class InitializeS3BucketsCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            resp = await s3_client.list_buckets()
            # names of currently existing buckets in s3
            bucket_names = [b['Name'] for b in resp['Buckets']]
            # all buckets we need for the API to run
            api_buckets = ['tournaments', 'series', 'templates']
            # create buckets if they can't be found in s3
            for bucket in api_buckets:
                if bucket not in bucket_names:
                    await s3_client.create_bucket(Bucket=bucket)

@dataclass
class ReadFileInS3BucketCommand(Command[str]):
    bucket: str
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            response = await s3_client.get_object(Bucket=self.bucket, Key=self.file_name)
            async with response['Body'] as stream:
                object_data: str = await stream.read()
                return object_data

@dataclass
class WriteMessageToFileInS3BucketCommand(Command[str]):
    bucket: str
    file_name: str
    message: bytes

    async def handle(self, db_wrapper, s3_wrapper):
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            object_data: str = await s3_client.put_object(Bucket=self.bucket, Key=self.file_name, Body=self.message)
            return object_data

@dataclass 
class GetUserIdFromSessionCommand(Command[User | None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            user_id = int(row[0])
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()

            player_id = int(row[0])
            
            return User(user_id, player_id)

@dataclass
class GetUserWithPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                JOIN sessions s on s.user_id = u.id
                JOIN role_permissions rp on rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ?
                LIMIT 1""", (self.session_id, self.permission_name)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            return User(int(row[0]), int(row[1]))
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])

@dataclass
class GetUserDataFromEmailCommand(Command[UserLoginData | None]):
    email: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, password_hash FROM users WHERE email = ?", (self.email, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return UserLoginData(int(row[0]), self.email, str(row[2]))
            
@dataclass
class CreateSessionCommand(Command[None]):
    session_id: str
    user_id: int
    expires_on: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            command = "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)"
            async with db.execute(command, (self.session_id, self.user_id, self.expires_on)) as cursor:
                rows_inserted = cursor.rowcount

            # TODO: Run queries to identify why session creation failed
            if rows_inserted != 1:
                raise Problem("Failed to create session")
                
            await db.commit()
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))
            await db.commit()

@dataclass
class CreateUserCommand(Command[User]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            row = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (self.email, self.password_hash))

            # TODO: Run queries to identify why user creation failed
            if row is None:
                raise Problem("Failed to create user")

            await db.commit()
            return User(int(row[0]), None)
        
@dataclass
class CreatePlayerCommand(Command[Player]):
    user_id: int | None
    data: CreatePlayerRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        async with db_wrapper.connect() as db:
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, discord_id) 
                VALUES (?, ?, ?, ?, ?, ?)"""
            player_id = await db.execute_insert(
                command, 
                (data.name, data.country_code, data.is_hidden, data.is_shadow, data.is_banned, data.discord_id))
            
            # TODO: Run queries to determine why it errored
            if player_id is None:
                raise Problem("Failed to create player")

            if self.user_id is not None:
                async with db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id)) as cursor:
                    # handle case where user with the given ID doesn't exist
                    if cursor.rowcount != 1:
                        raise Problem("Invalid User ID", status=404)

            await db.commit()
            return Player(int(player_id[0]), data.name, data.country_code, data.is_hidden, data.is_shadow, data.is_banned, data.discord_id)

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
            
            fc_query = "SELECT game, fc, is_verified FROM friend_codes WHERE player_id = ?"
            friend_code_rows = await db.execute_fetchall(fc_query, (self.id, ))
            friend_codes = [FriendCode(fc, game, self.id, bool(is_verified)) for game, fc, is_verified in friend_code_rows]

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

@dataclass
class GrantRoleCommand(Command[None]):
    granter_user_id: int
    target_user_id: int
    role: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        # For now, the rules about which roles can grant other roles is defined here, but we could move it to  the database
        # in the future.
        if self.role in [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]:
            allowed_roles = [roles.SUPER_ADMINISTRATOR]
        else:
            allowed_roles = [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]

        allowed_role_ids = [roles.id_by_default_role[role] for role in allowed_roles]

        async with db_wrapper.connect() as db:
            async with db.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    JOIN users u on ur.user_id = u.id
                    WHERE u.id = ? AND r.id IN ({','.join(map(str, allowed_role_ids))})
                )""", (self.granter_user_id,)) as cursor:
                row = await cursor.fetchone()
                can_grant = row is not None and bool(row[0])

            if not can_grant:
                raise Problem("Not authorized to grant role", status=401)

            try:
                async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                    row = await cursor.fetchone()
                    role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)

                await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)", (self.target_user_id, role_id))
                await db.commit()
            except Exception as e:
                async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (self.target_user_id,)) as cursor:
                    row = await cursor.fetchone()
                    user_exists = row is not None

                if not user_exists:
                    raise Problem("User not found", status=404)
                else:
                    raise Problem("Unexpected error")

@dataclass
class RegisterPlayerCommand(Command[None]):
    player_id: int
    tournament_id: int
    squad_id: int | None
    is_squad_captain: bool
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    is_invite: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        timestamp = int(datetime.utcnow().timestamp())
        async with db_wrapper.connect() as db:
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (self.player_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
                    if not existing_squad_id:
                        raise Problem("Player already registered for tournament", status=400)
            if existing_squad_id:
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE squad_id = ?", (existing_squad_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    is_registered = row[0]
                    if is_registered == 1:
                        raise Problem('Player is already registered for this tournament', status=400)
            # check if mii name is required and if player's squad is at maximum number of players
            if self.squad_id is not None:
                async with db.execute("SELECT max_squad_size, mii_name_required FROM tournaments WHERE id = ?", (self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    max_squad_size = row[0]
                    mii_name_required = row[1]
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem('Tournament requires a Mii Name', status=400)
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id = ?", (self.tournament_id, self.squad_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size == max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
            async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, self.squad_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, self.is_invite)) as cursor:
                tournament_player_id = cursor.lastrowid
            await db.commit()

@dataclass
class CreateSquadCommand(Command[None]):
    squad_name: str | None
    squad_tag: str | None
    squad_color: str
    player_id: int
    tournament_id: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    admin: bool = False

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        timestamp = int(datetime.utcnow().timestamp())
        is_registered = 1
        is_squad_captain = 1
        is_invite = 0
        async with db_wrapper.connect() as db:
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (self.player_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
            if existing_squad_id is not None:
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE squad_id = ?", (existing_squad_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    is_registered = row[0]
                    if is_registered == 1:
                        raise Problem('Player is already registered for this tournament', status=400)
            # check if tournament registrations are open
            async with db.execute("SELECT is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required FROM tournaments WHERE ID = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                is_squad = row[0]
                registrations_open = row[1]
                squad_tag_required = row[2]
                squad_name_required = row[3]
                mii_name_required = row[4]
                if is_squad == 0:
                    raise Problem('This is not a squad tournament', status=400)
                if self.admin is False and registrations_open == 0:
                    raise Problem('Tournament registrations are closed', status=400)
                if squad_tag_required == 1 and self.squad_tag is None:
                    raise Problem('Tournament requires a tag for squads', status=400)
                if squad_name_required == 1 and self.squad_name is None:
                    raise Problem('Tournament requires a name for squads', status=400)
                if mii_name_required == 1 and self.mii_name is None:
                    raise Problem('Tournament requires a Mii Name', status=400)
            async with db.execute("""INSERT INTO tournament_squads(name, tag, color, timestamp, tournament_id, is_registered)
                VALUES (?, ?, ?, ?, ?, ?)""", (self.squad_name, self.squad_tag, self.squad_color, timestamp, self.tournament_id, is_registered)) as cursor:
                squad_id = cursor.lastrowid
            await db.commit()

            async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, squad_id, is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, is_invite)) as cursor:
                tournament_player_id = cursor.lastrowid
            await db.commit()

@dataclass
class GetPlayerIdForUserCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int:
        async with db_wrapper.connect() as db:
            # get player id from user id in request
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("User does not exist", status=404)

                return int(row[0])

@dataclass
class EditSquadCommand(Command[None]):
    tournament_id: int
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: str
    is_registered: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE tournament_squads SET name = ?, tag = ?, color = ?, is_registered = ? WHERE id = ? AND tournament_id = ?",
                (self.squad_name, self.squad_tag, self.squad_color, self.is_registered, self.squad_id, self.tournament_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem("Squad not found", status=404)
            await db.commit()