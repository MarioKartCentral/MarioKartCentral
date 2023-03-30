from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar
import aiobotocore.session
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
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        db_wrapper.reset_db()

class InitializeDbSchemaCommand(Command[None]):
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("pragma journal_mode = WAL;")
            await db.execute("pragma synchronous = NORMAL;")
            for table in tables.all_tables:
                await db.execute(table.get_create_table_command())
            await db.commit()

@dataclass
class SeedDatabaseCommand(Command[None]):
    admin_email: str
    hashed_pw: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        from api.auth import permissions, roles
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
            
            await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?) ON CONFLICT DO NOTHING", (self.admin_email, self.hashed_pw))
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

            await db.commit()

class InitializeS3BucketsCommand(Command[None]):
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
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

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            response = await s3_client.get_object(Bucket=self.bucket, Key=self.file_name)
            async with response['Body'] as stream:
                return await stream.read()

@dataclass
class WriteMessageToFileInS3BucketCommand(Command[str]):
    bucket: str
    file_name: str
    message: bytes

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            return await s3_client.put_object(Bucket=self.bucket, Key=self.file_name, Body=self.message)

@dataclass 
class GetUserIdFromSessionCommand(Command[int | None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return int(row[0])

@dataclass
class GetUserWithPermissionFromSessionCommand(Command[int | None]):
    session_id: str
    permission_name: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int | None:
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id FROM roles r
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

            return int(row[0])
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> bool:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])

@dataclass
class GetUserDataFromEmailCommand(Command[UserLoginData | None]):
    email: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, password_hash FROM users WHERE email = ?", (self.email, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return UserLoginData(int(row[0]), self.email, str(row[2]))
            
@dataclass
class CreateSessionCommand(Command[None | Error]):
    session_id: str
    user_id: int
    expires_on: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            command = "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)"
            async with db.execute(command, (self.session_id, self.user_id, self.expires_on)) as cursor:
                rows_inserted = cursor.rowcount

            # TODO: Run queries to identify why session creation failed
            if rows_inserted != 1:
                return Error("Failed to create session")
                
            await db.commit()
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))
            await db.commit()

@dataclass
class CreateUserCommand(Command[User | Error]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            row = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (self.email, self.password_hash))

            # TODO: Run queries to identify why user creation failed
            if row is None:
                return Error("Failed to create user")

            await db.commit()
            return User(int(row[0]))
        
@dataclass
class CreatePlayerCommand(Command[Player | Error]):
    name: str
    user_id: int | None
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            command = """INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, discord_id) 
                VALUES (?, ?, ?, ?, ?, ?)"""
            player_id = await db.execute_insert(
                command, 
                (self.name, self.country_code, self.is_hidden, self.is_shadow, self.is_banned, self.discord_id))
            
            # TODO: Run queries to determine why it errored
            if player_id is None:
                return Error("Failed to create player")

            if self.user_id is not None:
                async with db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id)) as cursor:
                    # handle case where user with the given ID doesn't exist
                    if cursor.rowcount != 1:
                        return Error("Invalid User ID")

            await db.commit()
            return Player(int(player_id[0]), self.name, self.country_code, self.is_hidden, self.is_shadow, self.is_banned, self.discord_id)

@dataclass
class UpdatePlayerCommand(Command[bool]):
    id: int
    name: str
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> bool:
        async with db_wrapper.connect() as db:
            update_query = """UPDATE players 
            SET name = ?, country_code = ?, is_hidden = ?, is_shadow = ?, is_banned = ?, discord_id = ?
            WHERE id = ?"""
            params = (self.name, self.country_code, self.is_hidden, self.is_shadow, self.is_banned, self.discord_id, self.id)

            async with db.execute(update_query, params) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True


@dataclass
class GetPlayerDetailedCommand(Command[PlayerDetailed | None]):
    id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
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
            
            user = None if user_row is None else User(int(user_row[0]))

            return PlayerDetailed(self.id, name, country_code, is_hidden, is_shadow, is_banned, discord_id, friend_codes, user)