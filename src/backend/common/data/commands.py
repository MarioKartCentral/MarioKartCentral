from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar
from common.auth import roles, permissions
import common.data.db.tables as tables
from common.data.db import DBWrapper
from common.data.s3 import S3Wrapper
from common.data.models import *
import msgspec

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
        bucket_names = await s3_wrapper.list_buckets()

        # all buckets we need for the API to run
        api_buckets = ['tournaments', 'series', 'templates']
        for bucket in api_buckets:
            if bucket not in bucket_names:
                await s3_wrapper.create_bucket(bucket)

@dataclass
class ReadFileInS3BucketCommand(Command[bytes | None]):
    bucket: str
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        return await s3_wrapper.get_object(self.bucket, self.file_name)

@dataclass
class WriteMessageToFileInS3BucketCommand(Command[None]):
    bucket: str
    file_name: str
    message: bytes

    async def handle(self, db_wrapper, s3_wrapper):
        await s3_wrapper.put_object(self.bucket, self.file_name, self.message)

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
            assert row is not None
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
            
            return UserLoginData(int(row[0]), int(row[1]), self.email, str(row[2]))

@dataclass
class GetUserDataFromIdCommand(Command[User | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id FROM users WHERE id = ?", (self.id, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return User(int(row[0]), int(row[1]))
            
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
    selected_fc_id: int | None
    is_privileged: bool #if True, bypasses check for tournament registrations being open

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        timestamp = int(datetime.utcnow().timestamp())
        async with db_wrapper.connect() as db:
            # check if registrations are open and if mii name is required
            async with db.execute("SELECT max_squad_size, mii_name_required, registrations_open FROM tournaments WHERE id = ?", (self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                max_squad_size, mii_name_required, registrations_open = row
                if (not registrations_open) and (not self.is_privileged):
                    raise Problem("Tournament registrations are closed", status=400)
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
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
                    if is_registered == 1 and (not self.is_invite): # should still be able to invite someone if they are registered for the tournament
                        raise Problem('Player is already registered for this tournament', status=400)
            # check if player's squad is at maximum number of players
            if self.squad_id is not None and max_squad_size is not None:
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id = ?", (self.tournament_id, self.squad_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size >= max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, self.squad_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, 
                self.is_invite, self.selected_fc_id))
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
    selected_fc_id: int | None
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

            async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, squad_id, is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, is_invite,
                self.selected_fc_id)) as cursor:
                tournament_player_id = cursor.lastrowid
            await db.commit()

@dataclass
class GetPlayerIdForUserCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> int:
        async with db_wrapper.connect(readonly=True) as db:
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

@dataclass
class CheckSquadCaptainPermissionsCommand(Command[None]):
    tournament_id: int
    squad_id: int
    captain_player_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # check captain's permissions
            async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = ?", 
                (self.captain_player_id, self.tournament_id, 0)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("You are not registered for this tournament", status=400)
                captain_squad_id, is_squad_captain = row
                if captain_squad_id != self.squad_id:
                    raise Problem("You are not registered for this squad", status=400)
                if is_squad_captain == 0:
                    raise Problem("You are not captain of this squad", status=400)

@dataclass
class EditPlayerRegistrationCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
    player_id: int
    mii_name: str | None
    can_host: bool
    is_invite: bool
    is_checked_in: bool
    is_squad_captain: bool
    selected_fc_id: int | None
    is_privileged: bool
    
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open, mii_name_required FROM tournaments WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                registrations_open, mii_name_required = row
                # make sure players can't edit their registration details after registrations have closed
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so you cannot edit your registration details", status=400)
                # check for validity of mii name field
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
            #check if registration exists
            async with db.execute("SELECT id, is_invite FROM tournament_players WHERE tournament_id = ? AND squad_id = ? AND player_id = ?",
                (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Registration not found", status=404)
                registration_id, curr_is_invite = row
            # if a player accepts an invite while already registered for a different squad, their old registration must be removed
            if curr_is_invite and (not self.is_invite):
                await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND is_invite = ?",
                    (self.tournament_id, self.player_id, False))
            await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, selected_fc_id = ? WHERE id = ?", (
                self.mii_name, self.can_host, self.is_invite, self.is_checked_in, self.is_squad_captain, self.selected_fc_id, registration_id))

@dataclass
class UnregisterPlayerCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
    player_id: int
    is_privileged: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open FROM tournaments WHERE tournament_id = ?", (self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                registrations_open = row[0]
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so players cannot be unregistered from this tournament", status=400)
            await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id = ? AND player_id = ?", (self.tournament_id, self.squad_id, self.tournament_id))

@dataclass
class GetSquadDetailsCommand(Command[TournamentSquadDetails]):
    tournament_id: int
    squad_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ?, squad_id = ?",
                (self.tournament_id, self.squad_id)) as cursor:
                squad_row = await cursor.fetchone()
                if not squad_row:
                    raise Problem("Squad not found", status=404)
                squad_id, name, tag, color, timestamp, is_registered = squad_row
            async with db.execute("""SELECT t.player_id, t.is_squad_captain, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.squad_id = ?""",
                                    (self.squad_id)) as cursor:
                player_rows = await cursor.fetchall()
                players = []
                player_dict = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve
                for row in player_rows:
                    player_id, is_squad_captain, player_timestamp, is_checked_in, mii_name, can_host, is_invite, curr_fc_id, player_name, country, discord_id = row
                    curr_player = SquadPlayerDetails(player_id, player_timestamp, is_checked_in, mii_name, can_host,
                        player_name, country, discord_id, [], is_squad_captain, is_invite)
                    players.append(curr_player)

                    player_dict[curr_player.player_id] = curr_player
                    fc_id_list.append(curr_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament
            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN {','.join(map(str, player_dict.keys()))}{fc_where_clause}"
            async with db.execute(fc_query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
            return TournamentSquadDetails(squad_id, name, tag, color, timestamp, is_registered, players)

@dataclass
class CheckIfSquadTournament(Command[bool]):
    tournament_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
                return bool(is_squad)

@dataclass
class GetSquadRegistrationsCommand(Command[List[TournamentSquadDetails]]):
    tournament_id: int
    eligible_only: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            where_clause = ""
            if self.eligible_only:
                where_clause = "AND is_registered = 1"
            async with db.execute(f"SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? {where_clause}", (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                squads = {}
                for row in rows:
                    squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered = row
                    curr_squad = TournamentSquadDetails(squad_id, squad_name, squad_tag, squad_color, squad_timestamp, is_registered, [])
                    squads[squad_id] = curr_squad
            async with db.execute("""SELECT t.player_id, t.squad_id, t.is_squad_captain, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                player_dict = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve
                for row in rows:
                    player_id, squad_id, is_squad_captain, player_timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, player_name, country, discord_id = row
                    if squad_id not in squads:
                        continue
                    curr_player = SquadPlayerDetails(player_id, player_timestamp, is_checked_in, mii_name, can_host, player_name, country, discord_id, [], is_squad_captain, is_invite)
                    curr_squad = squads[squad_id]
                    curr_squad.players.append(curr_player)

                    player_dict[player_id] = curr_player
                    fc_id_list.append(selected_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament
            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN {','.join(map(str, player_dict.keys()))}{fc_where_clause}"
            async with db.execute(fc_query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
        return list(squads.values())
    
@dataclass
class GetFFARegistrationsCommand(Command[List[TournamentPlayerDetails]]):
    tournament_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT t.player_id, t.timestamp, t.is_checked_in, t.mii_name, t.can_host, t.selected_fc_id,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.tournament_id = ?""",
                                    (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                players = []

                player_dict = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve

                for row in rows:
                    player_id, player_timestamp, is_checked_in, mii_name, can_host, selected_fc_id, name, country, discord_id = row
                    curr_player = TournamentPlayerDetails(player_id, player_timestamp, is_checked_in, mii_name, can_host, name, country, discord_id, [])
                    players.append(curr_player)
                    
                    player_dict[player_id] = curr_player
                    fc_id_list.append(selected_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament

            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE tournament_id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN {','.join(map(str, player_dict.keys()))}{fc_where_clause}"
            async with db.execute(fc_query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
                return players
            
@dataclass
class CreateTournamentCommand(Command[None]):
    body: CreateTournamentRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        # store minimal data about each tournament in the SQLite DB
        async with db_wrapper.connect() as db:
            b = self.body
            cursor = await db.execute(
                """INSERT INTO tournaments(
                    name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, use_series_description, series_stats_include,
                    logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                    squad_name_required, mii_name_required, host_status_required, checkins_open, min_players_checkin, verified_fc_required, is_viewable, is_public,
                    show_on_profiles, require_single_fc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.tournament_name, b.game, b.mode, b.series_id, b.is_squad, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description,
                b.series_stats_include, b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open, b.min_players_checkin,
                b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, b.require_single_fc))
            tournament_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('tournaments', f'{tournament_id}.json', s3_message)
            
@dataclass
class EditTournamentCommand(Command[None]):
    body: EditTournamentRequestData
    id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            b = self.body
            cursor = await db.execute("""UPDATE tournaments
                SET name = ?,
                series_id = ?,
                registrations_open = ?,
                date_start = ?,
                date_end = ?,
                description = ?,
                use_series_description = ?,
                series_stats_include = ?,
                logo = ?,
                url = ?,
                registration_deadline = ?,
                registration_cap = ?,
                teams_allowed = ?,
                teams_only = ?,
                team_members_only = ?,
                min_squad_size = ?,
                max_squad_size = ?,
                squad_tag_required = ?,
                squad_name_required = ?,
                mii_name_required = ?,
                host_status_required = ?,
                checkins_open = ?,
                min_players_checkin = ?,
                verified_fc_required = ?,
                is_viewable = ?,
                is_public = ?,
                show_on_profiles = ?,
                WHERE id = ?""",
                (b.tournament_name, b.series_id, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description, b.series_stats_include,
                b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open,
                b.min_players_checkin, b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, self.id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No tournament found', status=404)
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('tournaments', f'{self.id}.json', s3_message)
    
@dataclass
class GetTournamentDataCommand(Command[CreateTournamentRequestData]):
    id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        body = await s3_wrapper.get_object('tournaments', f'{self.id}.json')
        if body is None:
            raise Problem('No tournament found', status=404)
        tournament_data = msgspec.json.decode(body, type=CreateTournamentRequestData)
        return tournament_data

@dataclass
class GetTournamentListCommand(Command[List[TournamentDataMinimal]]):
    filter: TournamentFilter

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        filter = self.filter
        is_minimal = filter.is_minimal
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
            append_equal_filter(filter.mode, "mode")
            append_equal_filter(filter.series_id, "series_id")
            append_equal_filter(filter.is_public, "is_public")
            append_equal_filter(filter.is_viewable, "is_viewable")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            if is_minimal:
                tournaments_query = f"SELECT id, name, game, mode, date_start, date_end FROM tournaments{where_clause}"
            else:
                tournaments_query = f"SELECT id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, description, logo FROM tournaments{where_clause}"
            
            tournaments = []
            async with db.execute(tournaments_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    if is_minimal:
                        tournament_id, name, game, mode, date_start, date_end = row
                        tournaments.append(TournamentDataMinimal(tournament_id, name, game, mode, date_start, date_end))
                    else:
                        tournament_id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, description, logo = row
                        tournaments.append(TournamentDataBasic(tournament_id, name, game, mode, date_start, date_end, series_id,
                            bool(is_squad), bool(registrations_open), description, logo))
            return tournaments

@dataclass
class CreateSeriesCommand(Command[None]):
    body: SeriesRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body
        # store minimal data about each series in the SQLite DB
        async with db_wrapper.connect() as db:
            cursor = await db.execute(
                "INSERT INTO tournament_series(name, url, game, mode, is_historical, is_public, description, logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (b.series_name, b.url, b.game, b.mode, b.is_historical, b.is_public, b.description, b.logo))
            series_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('series', f'{series_id}.json', s3_message)

@dataclass
class EditSeriesCommand(Command[None]):
    body: SeriesRequestData
    series_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body
        async with db_wrapper.connect() as db:
            cursor = await db.execute("""UPDATE tournament_series
                SET name = ?,
                url = ?,
                game = ?,
                mode = ?,
                is_historical = ?,
                is_public = ?,
                description = ?,
                logo = ?
                WHERE id = ?""",
                (b.series_name, b.url, b.game, b.mode, b.is_historical, b.is_public, b.description, b.logo, self.series_id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No series found', status=404)
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('series', f'{self.series_id}.json', s3_message)

@dataclass
class GetSeriesDataCommand(Command[Series]):
    series_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        body = await s3_wrapper.get_object('series', f'{self.series_id}.json')
        if body is None:
            raise Problem('No series found', status=404)
        series_data = msgspec.json.decode(body, type=Series)
        return series_data

@dataclass
class GetSeriesListCommand(Command[List[Series]]):
    filter: SeriesFilter

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.mode, "mode")
            append_equal_filter(filter.is_public, "is_public")
            append_equal_filter(filter.is_historical, "is_historical")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"

            series_query = f"SELECT id, name, url, game, mode, is_historical, is_public, description, logo FROM tournament_series{where_clause}"

            series = []
            async with db.execute(series_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    series_id, series_name, url, game, mode, is_historical, is_public, description, logo = row
                    series.append(Series(series_id, series_name, url, game, mode, bool(is_historical), bool(is_public), description, logo))
            return series

@dataclass
class CreateTournamentTemplateCommand(Command[None]):
    body: TournamentTemplateRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body

        # we only need to put the template name and series ID into the database for querying, the rest can go into s3 since we won't be querying this
        async with db_wrapper.connect() as db:
            cursor = await db.execute("INSERT INTO tournament_templates (name, series_id) VALUES (?, ?)",
            (b.template_name, b.series_id))
            template_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('templates', f'{template_id}.json', s3_message)

@dataclass
class EditTournamentTemplateCommand(Command[None]):
    body: TournamentTemplateRequestData
    template_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body

        async with db_wrapper.connect() as db:
            cursor = await db.execute("""UPDATE tournament_templates
                SET name = ?,
                series_id = ?
                WHERE id = ?""", (b.template_name, b.series_id, self.template_id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No template found', status=404)
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('templates', f'{self.template_id}.json', s3_message)

@dataclass
class GetTournamentTemplateDataCommand(Command[TournamentTemplate]):
    template_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        body = await s3_wrapper.get_object('templates', f'{self.template_id}.json')
        if body is None:
            raise Problem('No template found', status=404)
        template_data = msgspec.json.decode(body, type=TournamentTemplate)
        template_data.id = self.template_id
        return template_data

@dataclass
class GetTournamentTemplateListCommand(Command[List[TournamentTemplateMinimal]]):
    filter: TemplateFilter

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            append_equal_filter(filter.series_id, "series_id")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"

            template_query = f"SELECT id, name, series_id FROM tournament_templates{where_clause}"

            templates = []
            async with db.execute(template_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    template_id, template_name, series_id = row
                    templates.append(TournamentTemplateMinimal(template_id, template_name, series_id))
            return templates
            

@dataclass
class CreateUserSettingsCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("INSERT INTO user_settings(user_id) VALUES (?)", (self.user_id,)) as cursor:
                rows_inserted = cursor.rowcount

            if rows_inserted != 1:
                raise Problem("Failed to create user settings")
            
            await db.commit()

@dataclass
class GetUserSettingsCommand(Command[UserSettings | None]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT avatar, discord_tag, about_me, language, 
                color_scheme, timezone FROM user_settings WHERE user_id = ?""", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
        avatar, discord_tag, about_me, language, color_scheme, timezone = row

        return UserSettings(self.user_id, avatar, discord_tag, about_me, language, color_scheme, timezone)
    
@dataclass
class EditUserSettingsCommand(Command[bool]):
    user_id: int
    data: EditUserSettingsRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        data = self.data
        set_clauses = []
        variable_parameters = []

        def set_value(value, column_name):
            if value is not None:
                set_clauses.append(f"{column_name} = ?")
                variable_parameters.append(value)

        set_value(data.avatar, "avatar")
        set_value(data.discord_tag, "discord_tag")
        set_value(data.about_me, "about_me")
        set_value(data.language, "language")
        set_value(data.color_scheme, "color_scheme")
        set_value(data.timezone, "timezone")

        if not set_clauses:
            raise Problem("Bad request body", detail="There are no values to set")

        async with db_wrapper.connect() as db:
            update_query = f"UPDATE user_settings SET {', '.join(set_clauses)} WHERE user_id = ?"""
            variable_parameters.append(self.user_id)
            async with db.execute(update_query, variable_parameters) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True

@dataclass
class GetNotificationsCommand(Command[List[Notification]]):
    user_id: int
    data: NotificationFilter

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        data = self.data

        where_clauses: list[str] = ['n.user_id = ?']
        where_params: list[Any]  = [self.user_id]

        if data.is_read is not None:
            where_clauses.append('n.is_read = ?')
            where_params.append(data.is_read)
        if data.type is not None:
            try:
                types = list(map(int, data.type.split(','))) # convert types to list of ints
                type_query = ['n.type = ?'] * len(types)
                where_clauses.append(f"({' OR '.join(type_query)})")
                where_params += types
            except Exception as e:
                raise Problem('Bad type query', detail=str(e), status=400)
        if data.before is not None:
            try:
                where_clauses.append('n.created_date < ?')
                where_params.append(int(data.before))
            except Exception as e:
                raise Problem('Bad before date query', detail=str(e),  status=400)
        if data.after is not None:
            try:
                where_clauses.append('n.created_date > ?')
                where_params.append(data.after)
            except Exception as e:
                raise Problem('Bad after date query', detail=str(e), status=400)

        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(f"""
                SELECT n.id, n.type, c.content, n.created_date, n.is_read FROM notifications n
                JOIN notification_content c ON n.content_id = c.id
                WHERE {' AND '.join(where_clauses)}""", tuple(where_params)) as cursor:

                return [Notification(row[0], row[1], row[2], row[3], bool(row[4])) for row in await cursor.fetchall()]

@dataclass
class MarkOneNotificationAsReadCommand(Command[int]):
    id: int
    user_id: int
    data: MarkAsReadRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        is_read = 1 if self.data.is_read else 0
        notification_id = self.id
        user_id = self.user_id

        async with db_wrapper.connect() as db:
            async with db.execute("""
                UPDATE notifications SET is_read = ?
                WHERE id = ? AND user_id = ?""", (is_read, notification_id, user_id)) as cursor:

                if cursor.rowcount == 1:
                    await db.commit()
                    return cursor.rowcount

            # either the notification does not exist, or the request user_id does not match notif user_id
            async with db.execute("SELECT EXISTS (SELECT 1 FROM notifications WHERE id = ?)", (notification_id, )) as cursor:
                row = await cursor.fetchone()
                notification_exists = row is not None and bool(row[0])

                if notification_exists:
                    raise Problem('User does not have permission', status=401)
                raise Problem('Unknown notification', status=404)

@dataclass
class MarkAllNotificationsAsReadCommand(Command[int]):
    user_id: int
    data: MarkAsReadRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        is_read = 1 if self.data.is_read else 0
        user_id = self.user_id

        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE notifications SET is_read = ? WHERE user_id = ?", (is_read, user_id)) as cursor:
                count = cursor.rowcount
                if count > 0:
                    await db.commit()
                return count
            
@dataclass
class GetUnreadNotificationsCountCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT COUNT (*) FROM notifications WHERE user_id = ? AND is_read = 0""", (self.user_id, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Unable to fetch unread notifications count")
                return int(row[0])

@dataclass
class DispatchNotificationsCommand(Command[int]):
    """
    Dispatch a notification to one or more users, and returns the numbers of notifications that were sent.

    content:
        The notification message to send. All users will be notified with the same content.

    notification_type:
        The type of the notification.

    user_ids:
        A list of one or more user IDs to dispatch to.
    """
    content: str
    user_ids: List[int]
    notification_type: int = 0

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            inserted_row = await db.execute_insert("INSERT INTO notification_content(content) VALUES (?)", (self.content, ))
            if inserted_row is None:
                raise Problem('Failed to insert notification content to db')
            
            content_id = int(inserted_row[0])
            await db.commit()

            user_ids = self.user_ids
            created_date = int(datetime.utcnow().timestamp())
            content_is_shared = int(len(user_ids) > 1)
            row_args = [(user_id, self.notification_type, content_id, created_date, content_is_shared) for user_id in user_ids]

            async with await db.executemany("INSERT INTO notifications(user_id, type, content_id, created_date, content_is_shared) VALUES (?, ?, ?, ?, ?)", row_args) as cursor:
                count = cursor.rowcount
                if count > 0:
                    await db.commit()

            return count

