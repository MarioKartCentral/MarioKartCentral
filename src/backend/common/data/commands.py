from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import aiobotocore.session
from common.data.db import DBWrapper
from common.data.db.models import *
from common.data.s3 import S3Wrapper


TCommandResponse = TypeVar('TCommandResponse')

# TODO: Split up this file into multiple files that handle specific areas (e.g. tournaments)

class Command(ABC, Generic[TCommandResponse]):
    @abstractmethod
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> TCommandResponse:
        pass

class ResetDbCommand(Command[None]):
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        db_wrapper.reset_db

class InitializeDbSchemaCommand(Command[None]):
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as conn:
            await conn.execute("pragma journal_mode = WAL;")
            await conn.execute("pragma synchronous = NORMAL;")
            await conn.execute(Player.get_create_table_command())
            await conn.execute(FriendCode.get_create_table_command())
            await conn.execute(User.get_create_table_command())
            await conn.execute(Session.get_create_table_command())
            await conn.execute(Role.get_create_table_command())
            await conn.execute(Permission.get_create_table_command())
            await conn.execute(UserRole.get_create_table_command())
            await conn.execute(RolePermission.get_create_table_command())
            await conn.execute(TournamentSeries.get_create_table_command())
            await conn.execute(Tournament.get_create_table_command())
            await conn.execute(TournamentTemplate.get_create_table_command())
            await conn.execute(TournamentSquad.get_create_table_command())
            await conn.execute(TournamentPlayer.get_create_table_command())

@dataclass
class SeedDatabaseCommand(Command[None]):
    admin_email: str
    hashed_pw: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        from api.auth import permissions, roles
        async with db_wrapper.connect() as conn:
            await conn.executemany(
                "INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_roles_by_id.items())
            
            await conn.executemany(
                "INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                permissions.permissions_by_id.items())
            
            await conn.executemany(
                "INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_role_permission_ids)
            
            await conn.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?) ON CONFLICT DO NOTHING", (self.admin_email, self.hashed_pw))
            await conn.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

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

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> str:
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

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> str:
        session = aiobotocore.session.get_session()
        async with s3_wrapper.create_client(session) as s3_client:
            return await s3_client.put_object(Bucket=self.bucket, Key=self.file_name, Body=self.message)

@dataclass 
class GetUserIdFromSessionCommand(Command[int | None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int | None:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (self.session_id,)) as cursor:
                row = await cursor.fetchone()
                return None if row is None else int(row[0])

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
                return None if row is None else int(row[0])
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> bool:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()
                return row is not None and bool(row[0])
            
@dataclass
class GetUserDataFromEmailCommandResponse:
    id: int
    player_id: int
    email: str
    password_hash: str

@dataclass
class GetUserDataFromEmailCommand(Command[GetUserDataFromEmailCommandResponse | None]):
    email: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> GetUserDataFromEmailCommandResponse | None:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, password_hash FROM users WHERE email = ?", (self.email, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
                return GetUserDataFromEmailCommandResponse(int(row[0]), int(row[1]), self.email, str(row[2]))
            
@dataclass
class CreateSessionCommand(Command[None]):
    session_id: str
    user_id: int
    expires_on: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            await db.execute(
                "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)", 
                (self.session_id, self.user_id, self.expires_on))
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))

@dataclass
class CreateUserCommand(Command[int | None]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int | None:
        async with db_wrapper.connect() as db:
            row = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (self.email, self.password_hash))
            return None if row is None else int(row[0])
        
@dataclass
class CreatePlayerCommand(Command[int | None]):
    name: str
    user_id: int
    country_code: str
    is_hidden: bool
    is_shadow: bool
    is_banned: bool
    discord_id: str
    switch_fc: str | None
    mkw_fc: str | None
    mkt_fc: str | None
    nnid: str | None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int | None:
        async with db_wrapper.connect() as db:
            async with db.execute("""INSERT INTO players(name, country_code, is_hidden, is_shadow, is_banned, discord_id)
                VALUES (?, ?, ?, ?, ?, ?)""", (self.name, self.country_code, self.is_hidden, self.is_shadow, self.is_banned, self.discord_id)) as cursor:
                player_id = cursor.lastrowid
            await db.commit()

            await db.execute("UPDATE users SET player_id = ? WHERE id = ?", (player_id, self.user_id))
            # building a query to insert multiple rows to friend codes table
            fc_variable_parameters = []
            if self.switch_fc is not None:
                fc_variable_parameters.append((player_id, self.switch_fc, 1, 'MK8DX'))
            if self.mkw_fc is not None:
                fc_variable_parameters.append((player_id, self.mkw_fc, 0, 'MKW'))
            if self.mkt_fc is not None:
                fc_variable_parameters.append([player_id, self.mkt_fc, 1, 'MKT'])
            if self.nnid is not None:
                fc_variable_parameters.append([player_id, self.nnid, 1, 'MK8'])
            await db.executemany("INSERT INTO friend_codes VALUES (?, ?, ?, ?)", fc_variable_parameters)
            await db.commit()

            return player_id
