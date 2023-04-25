from dataclasses import dataclass, asdict
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
            await db.commit()

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
            player_id = row[0]
            
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

            return User(int(row[0]), row[1])
        
@dataclass
class GetUserWithTeamPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str
    team_id: int
    
    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM roles r
                JOIN user_team_roles ur ON ur.role_id = r.id
                JOIN users u ON ur.user_id = u.id
                JOIN sessions s ON s.user_id = u.id
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ? AND ur.team_id = ?
                LIMIT 1""", (self.session_id, self.permission_name, self.team_id)) as cursor:
                row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return User(int(row[0]), row[1])
            
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
            
            return UserLoginData(int(row[0]), row[1], self.email, str(row[2]))

@dataclass
class GetUserDataFromIdCommand(Command[User | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id FROM users WHERE id = ?", (self.id, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return User(int(row[0]), row[1])
            
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
    is_representative: bool
    is_privileged: bool #if True, bypasses check for tournament registrations being open

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        timestamp = int(datetime.utcnow().timestamp())
        async with db_wrapper.connect() as db:
            # check if registrations are open and if mii name is required
            async with db.execute("SELECT is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad, max_squad_size, mii_name_required, registrations_open, team_members_only = row
                if bool(is_squad) and self.squad_id is None:
                    raise Problem("Players may not register alone for squad tournaments", status=400)
                if not bool(is_squad) and self.squad_id is not None:
                    raise Problem("Players may not register for a squad for solo tournaments", status=400)
                if (not registrations_open) and (not self.is_privileged):
                    raise Problem("Tournament registrations are closed", status=400)
                if (not self.is_invite):
                    if mii_name_required == 1 and self.mii_name is None:
                        raise Problem("Tournament requires a Mii Name", status=400)
                    if mii_name_required == 0 and self.mii_name:
                        raise Problem("Tournament should not have a Mii Name", status=400)
                    
            # check if player exists if we are force-registering them
            if not self.is_privileged:
                async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player not found", status=404)
            
            # check if squad exists and if we are using the squad's tag in our mii name
            if self.squad_id is not None:
                async with db.execute("SELECT tag FROM tournament_squads WHERE id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Squad not found", status=404)
                    squad_tag = row[0]
                    if squad_tag is not None and self.mii_name is not None:
                        if squad_tag not in self.mii_name:
                            raise Problem("Mii name must contain squad tag", status=400)
                        
            # make sure the player is in a team roster that is linked to the current squad
            if bool(team_members_only):
                async with db.execute("""SELECT m.id FROM team_members m
                    JOIN team_squad_registrations r ON m.roster_id = r.roster_id
                    WHERE m.player_id = ? AND m.leave_date = ? AND r.squad_id IS ?""",
                    (self.player_id, None, self.squad_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player must be registered for a team roster linked to this squad", status=400)
                    
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (self.player_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
                    # if row exists but existing_squad_id is None, it's a FFA and theyre already registered
                    if not existing_squad_id:
                        raise Problem("Player already registered for tournament", status=400)
            if existing_squad_id:
                if existing_squad_id == self.squad_id:
                    raise Problem("Player is already invited to/registered for this squad", status=400)
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE id IS ?", (existing_squad_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    is_registered = row[0]
                    print(is_registered)
                    if is_registered == 1 and (not self.is_invite): # should still be able to invite someone if they are registered for the tournament
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            # check if player's squad is at maximum number of players
            if self.squad_id is not None and max_squad_size is not None:
                async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id IS ?", (self.tournament_id, self.squad_id)) as cursor:
                    player_squad_size = cursor.rowcount
                    if player_squad_size >= max_squad_size:
                        raise Problem('Squad at maximum number of players', status=400)
                    
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.player_id, self.tournament_id, self.squad_id, self.is_squad_captain, timestamp, self.is_checked_in, self.mii_name, self.can_host, 
                self.is_invite, self.selected_fc_id, self.is_representative))
            await db.commit()

@dataclass
class CreateSquadCommand(Command[None]):
    squad_name: str | None
    squad_tag: str | None
    squad_color: str
    creator_player_id: int # person who created the squad, may be different from the squad captain (ex. team tournaments where a team manager registers a squad they aren't in)
    captain_player_id: int # captain of the squad
    tournament_id: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    roster_ids: List[int]
    representative_ids: List[int]
    admin: bool = False

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper) -> None:
        timestamp = int(datetime.utcnow().timestamp())
        is_registered = True
        is_invite = False
        if len(set(self.roster_ids)) < len(self.roster_ids):
            raise Problem('Duplicate roster IDs detected', status=400)
        async with db_wrapper.connect() as db:
            # check if tournament registrations are open and that our arguments are correct for the current tournament
            async with db.execute("SELECT is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_allowed, teams_only, min_representatives FROM tournaments WHERE ID = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_allowed, teams_only, min_representatives = row
                if not bool(is_squad):
                    raise Problem('This is not a squad tournament', status=400)
                if self.admin is False and not bool(registrations_open):
                    raise Problem('Tournament registrations are closed', status=400)
                if bool(squad_tag_required) and self.squad_tag is None:
                    raise Problem('Tournament requires a tag for squads', status=400)
                if bool(squad_name_required) and self.squad_name is None:
                    raise Problem('Tournament requires a name for squads', status=400)
                if bool(mii_name_required) and self.mii_name is None:
                    raise Problem('Tournament requires a Mii Name', status=400)
                if not bool(teams_allowed) and len(self.roster_ids) > 0:
                    raise Problem('Teams are not allowed for this tournament', status=400)
                if bool(teams_only) and len(self.roster_ids) == 0:
                    raise Problem('Must specify at least one team roster ID for this tournament', status=400)
                if len(self.representative_ids) + 1 < min_representatives:
                    raise Problem(f'Must have at least {min_representatives} representatives for this tournament', status=400)
                if self.squad_tag is not None and self.mii_name is not None:
                    if self.squad_tag not in self.mii_name:
                        raise Problem("Mii name must contain squad tag", status=400)
                
            # make sure creating player has permission for all rosters they are registering
            if len(self.roster_ids) > 0 and not self.admin:
                async with db.execute(f"""
                    SELECT tr.id FROM roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_rosters tr ON tr.team_id = ur.team_id
                    JOIN users u ON ur.user_id = u.id
                    JOIN players pl ON u.player_id = pl.id
                    JOIN role_permissions rp ON rp.role_id = r.id
                    JOIN permissions p ON rp.permission_id = p.id
                    WHERE pl.id = ? AND p.name = ? AND tr.id IN ({','.join([str(i) for i in self.roster_ids])})""",
                    (self.creator_player_id, permissions.REGISTER_TEAM_TOURNAMENT)) as cursor:
                    # get all of the roster IDs in our list that the player has permissions for
                    rows = await cursor.fetchall()
                    roster_permissions = set([row[0] for row in rows])
                    # check if there are any missing rosters that we don't have permission for
                    if len(roster_permissions) < len(self.roster_ids):
                        missing_rosters = [i for i in self.roster_ids if i not in roster_permissions]
                        raise Problem(f"Missing permissions for following rosters: {missing_rosters}")
                    
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (self.captain_player_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
            if existing_squad_id is not None:
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE id IS ?", (existing_squad_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    is_registered = row[0]
                    if is_registered == 1:
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            async with db.execute("""INSERT INTO tournament_squads(name, tag, color, timestamp, tournament_id, is_registered)
                VALUES (?, ?, ?, ?, ?, ?)""", (self.squad_name, self.squad_tag, self.squad_color, timestamp, self.tournament_id, is_registered)) as cursor:
                squad_id = cursor.lastrowid
            await db.commit()
            # find all players not already registered for a different (registered) squad which we can register for the tournament
            if len(self.roster_ids) > 0:
                async with db.execute(f"""
                    SELECT m.player_id FROM team_members m
                    WHERE m.roster_id IN ({','.join([str(i) for i in self.roster_ids])})
                    AND m.player_id NOT IN (SELECT t.player_id FROM tournament_players t
                        WHERE t.squad_id IN (SELECT s.id FROM tournament_squads s WHERE s.is_registered = 1)
                    )
                    """) as cursor:
                    rows = await cursor.fetchall()
                    valid_players = set([row[0] for row in rows])
                queries_parameters = []
                for p in valid_players:
                    if p == self.captain_player_id:
                        continue
                    if p in self.representative_ids:
                        is_representative = True
                    else:
                        is_representative = False
                    queries_parameters.append((p, self.tournament_id, squad_id, False, timestamp, self.is_checked_in, None, False, False, None, is_representative))
                await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", queries_parameters)
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.captain_player_id, self.tournament_id, squad_id, True, timestamp, self.is_checked_in, self.mii_name, self.can_host, is_invite,
                self.selected_fc_id, False))
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
                (self.captain_player_id, self.tournament_id, False)) as cursor:
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
    is_representative: bool | None
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
            async with db.execute("SELECT id, is_invite, is_representative FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?",
                (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Registration not found", status=404)
                registration_id, curr_is_invite, curr_is_rep = row
            if self.is_representative is None:
                self.is_representative = curr_is_rep
            # if a player accepts an invite while already registered for a different squad, their old registration must be removed
            if curr_is_invite and (not self.is_invite):
                await db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND is_invite = ?",
                    (self.tournament_id, self.player_id, False))
            await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ?, is_squad_captain = ?, selected_fc_id = ?, is_representative = ? WHERE id = ?", (
                self.mii_name, self.can_host, self.is_invite, self.is_checked_in, self.is_squad_captain, self.selected_fc_id, self.is_representative, registration_id))
            await db.commit()

@dataclass
class UnregisterPlayerCommand(Command[None]):
    tournament_id: int
    squad_id: int | None
    player_id: int
    is_privileged: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Tournament not found', status=404)
                registrations_open = row[0]
                if (not self.is_privileged) and (not registrations_open):
                    raise Problem("Registrations are closed, so players cannot be unregistered from this tournament", status=400)
            async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND squad_id IS ? AND player_id = ?", (self.tournament_id, self.squad_id, self.player_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Registration not found", status=404)
            # we should unregister a squad if it has no members remaining after this player is unregistered
            if self.squad_id is not None:
                async with db.execute("SELECT count(id) FROM tournament_players WHERE tournament_id = ? AND squad_id IS ?", (self.tournament_id, self.squad_id)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    num_squad_players = row[0]
                if num_squad_players == 0:
                    await db.execute("UPDATE tournament_squads SET is_registered = ? WHERE id = ?", (False, self.squad_id))
            await db.commit()

@dataclass
class GetSquadDetailsCommand(Command[TournamentSquadDetails]):
    tournament_id: int
    squad_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? AND id = ?",
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
                                    WHERE t.squad_id IS ?""",
                                    (self.squad_id,)) as cursor:
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
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
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
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
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

            # check if only single FCs are allowed or not and get the tournament's game
            async with db.execute("SELECT require_single_fc, game FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                game = row[1]
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT id, player_id, fc FROM friend_codes WHERE game = ? AND player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
            variable_parameters = (game,)
            async with db.execute(fc_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
                return players
            
@dataclass
class CreateTournamentCommand(Command[None]):
    body: CreateTournamentRequestData

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body
        # check for invalid body parameters
        if not b.is_squad and b.teams_allowed:
            raise Problem('Individual tournaments cannot have teams linked', status=400)
        if not b.teams_allowed and (b.teams_only or b.team_members_only):
            raise Problem('Non-team tournaments cannot have teams_only, team_members_only, min_representatives enabled', status=400)
        if not b.is_squad and (b.min_squad_size or b.max_squad_size or b.squad_tag_required or b.squad_name_required):
            raise Problem('Individual tournaments may not have settings for min_squad_size, max_squad_size, squad_tag_required, squad_name_required', status=400)
        if b.teams_allowed and (b.mii_name_required or b.host_status_required or b.require_single_fc):
            raise Problem('Team tournaments cannot have mii_name_required, host_status_required, or require_single_fc enabled', status=400)

        # store minimal data about each tournament in the SQLite DB
        async with db_wrapper.connect() as db:
            
            cursor = await db.execute(
                """INSERT INTO tournaments(
                    name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, use_series_description, series_stats_include,
                    logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                    squad_name_required, mii_name_required, host_status_required, checkins_open, min_players_checkin, verified_fc_required, is_viewable, is_public,
                    show_on_profiles, require_single_fc, min_representatives
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.tournament_name, b.game, b.mode, b.series_id, b.is_squad, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description,
                b.series_stats_include, b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open, b.min_players_checkin,
                b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, b.require_single_fc, b.min_representatives))
            tournament_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('tournaments', f'{tournament_id}.json', s3_message)
            
@dataclass
class EditTournamentCommand(Command[None]):
    body: EditTournamentRequestData
    id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        b = self.body
        
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
            if b.series_id:
                async with db.execute("SELECT id FROM tournament_series WHERE id = ?", (b.series_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise Problem("Series with provided ID cannot be found", status=404)
            # check for invalid body parameters
            if not is_squad and b.teams_allowed:
                raise Problem('Individual tournaments cannot have teams linked', status=400)
            if not b.teams_allowed and (b.teams_only or b.team_members_only):
                raise Problem('Non-team tournaments cannot have teams_only, team_members_only, min_representatives enabled', status=400)
            if not is_squad and (b.min_squad_size or b.max_squad_size or b.squad_tag_required or b.squad_name_required):
                raise Problem('Individual tournaments may not have settings for min_squad_size, max_squad_size, squad_tag_required, squad_name_required', status=400)
            if b.teams_allowed and (b.mii_name_required or b.host_status_required):
                raise Problem('Team tournaments cannot have mii_name_required, host_status_required, or require_single_fc enabled', status=400)
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
                min_representatives = ?
                WHERE id = ?""",
                (b.tournament_name, b.series_id, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description, b.series_stats_include,
                b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open,
                b.min_players_checkin, b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, b.min_representatives, self.id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No tournament found', status=404)
            

            s3_data = await s3_wrapper.get_object('tournaments', f'{self.id}.json')
            if s3_data is None:
                raise Problem("No tournament found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('tournaments', f'{self.id}.json', s3_message)

            await db.commit()

        
    
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
            

            s3_data = await s3_wrapper.get_object('series', f'{self.series_id}.json')
            if s3_data is None:
                raise Problem("No series found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('series', f'{self.series_id}.json', s3_message)

            await db.commit()

@dataclass
class GetSeriesDataCommand(Command[Dict[Any, Any]]):
    series_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        body = await s3_wrapper.get_object('series', f'{self.series_id}.json')
        if body is None:
            raise Problem('No series found', status=404)
        series_data = msgspec.json.decode(body)
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
            

            s3_data = await s3_wrapper.get_object('templates', f'{self.template_id}.json')
            if s3_data is None:
                raise Problem("No template found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('templates', f'{self.template_id}.json', s3_message)
            await db.commit()

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
class CreateTeamCommand(Command[None]):
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    approval_status: Approval
    is_historical: bool
    game: str
    mode: str
    is_recruiting: bool
    is_active: bool
    is_privileged: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            # we don't want users to be able to create teams that share the same name/tag as another team, but it should be possible if moderators wish
            if not self.is_privileged:
                async with db.execute("SELECT COUNT(id) FROM team_rosters WHERE name = ? OR tag = ?", (self.name, self.tag)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    if row[0] > 0:
                        raise Problem('An existing team already has this name or tag', status=400)
            creation_date = int(datetime.utcnow().timestamp())
            async with db.execute("""INSERT INTO teams (name, tag, description, creation_date, language, color, logo, approval_status, is_historical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.name, self.tag, self.description, creation_date, self.language, self.color, self.logo, self.approval_status,
                self.is_historical)) as cursor:
                team_id = cursor.lastrowid
            await db.commit()
            await db.execute("""INSERT INTO team_rosters(team_id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (team_id, self.game, self.mode, self.name, self.tag, creation_date, self.is_recruiting, self.is_active, self.approval_status))
            await db.commit()

@dataclass
class GetTeamInfoCommand(Command[Team]):
    team_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name, tag, description, creation_date, language, color, logo, approval_status, is_historical FROM teams WHERE id = ?",
                (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('Team not found', status=404)
                team_name, team_tag, description, team_date, language, color, logo, team_approval_status, is_historical = row
                team = Team(self.team_id, team_name, team_tag, description, team_date, language, color, logo, team_approval_status, is_historical, [])
            
            # get all rosters for our team
            rosters = []
            roster_dict = {}
            async with db.execute("SELECT id, game, mode, name, tag, creation_date, is_recruiting, approval_status FROM team_rosters WHERE team_id = ?",
                (self.team_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    roster_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, roster_approval_status = row
                    if roster_name is None:
                        roster_name = team_name
                    if roster_tag is None:
                        roster_tag = team_tag
                    curr_roster = TeamRoster(roster_id, self.team_id, game, mode, roster_name, roster_tag, roster_date, is_recruiting, roster_approval_status, [])
                    rosters.append(curr_roster)
                    roster_dict[curr_roster.id] = curr_roster
            
            team_members = []
            # get all current team members who are in a roster that belongs to our team
            roster_id_query = ','.join(map(str, roster_dict.keys()))
            async with db.execute(f"""SELECT player_id, roster_id, join_date
                                    FROM team_members
                                    WHERE roster_id IN ({roster_id_query}) AND leave_date = ?
                                    """, (None,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, roster_id, join_date = row
                    curr_team_member = PartialTeamMember(player_id, roster_id, join_date)
                    team_members.append(curr_team_member)

            player_dict = {}

            if len(team_members) > 0:
                # get info about all players who are in at least 1 roster on our team
                member_id_query = ','.join(set([str(m.player_id) for m in team_members]))
                async with db.execute(f"SELECT id, name, country_code, is_banned, discord_id FROM players WHERE id IN ({member_id_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        player_id, player_name, country, is_banned, discord_id = row
                        player_dict[player_id] = PartialPlayer(player_id, player_name, country, bool(is_banned), discord_id, [])

                # get all friend codes for members of our team that are from a game that our team has a roster for
                game_query = ','.join(set([r.game for r in rosters]))
                async with db.execute(f"SELECT player_id, game, fc, is_verified, is_primary FROM friend_codes WHERE player_id IN ({member_id_query}) AND game IN ({game_query})") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        player_id, game, fc, is_verified, is_primary = row
                        curr_fc = FriendCode(fc, game, player_id, bool(is_verified), bool(is_primary))
                        player_dict[player_id].friend_codes.append(curr_fc)

            for member in team_members:
                curr_roster = roster_dict[member.roster_id]
                p = player_dict[member.player_id]
                curr_player = RosterPlayerInfo(p.player_id, p.name, p.country_code, p.is_banned, p.discord_id, member.join_date,
                    [fc for fc in p.friend_codes if fc.game == curr_roster.game]) # only add FCs that are for the same game as current roster
                curr_roster.players.append(curr_player)

            team.rosters = rosters
            return team

@dataclass
class EditTeamCommand(Command[None]):
    team_id: int
    name: str
    tag: str
    description: str
    language: str
    color: int
    logo: str | None
    approval_status: Approval
    is_historical: bool
    game: str
    mode: str
    is_recruiting: bool
    is_active: bool
    is_privileged: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""UPDATE teams SET name = ?,
                tag = ?,
                description = ?,
                language = ?,
                color = ?,
                logo = ?,
                approval_status = ?,
                is_historical = ?,
                game = ?,
                mode = ?,
                is_recruiting = ?,
                is_active = ?
                WHERE id = ?""",
                (self.name, self.tag, self.description, self.language, self.color, self.logo, self.approval_status, self.is_historical,
                 self.game, self.mode, self.is_recruiting, self.is_active)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem('No team found', status=404)
                await db.commit()

@dataclass
class ManagerEditTeamCommand(Command[None]):
    team_id: int
    description: str
    language: str
    color: int
    logo: str | None
    is_recruiting: bool

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""UPDATE teams SET
                description = ?,
                language = ?,
                color = ?,
                logo = ?,
                is_recruiting = ?
                WHERE id = ?""",
                (self.description, self.language, self.color, self.logo, self.is_recruiting, self.team_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem('No team found', status=404)
                await db.commit()

@dataclass
class RequestEditTeamCommand(Command[None]):
    team_id: int
    name: str | None
    tag: str | None

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        if self.name is None and self.tag is None:
            raise Problem("Must request at least one of name/tag to be edited", status=400)
        async with db_wrapper.connect() as db:
            await db.execute("INSERT INTO team_edit_requests(team_id, name, tag) VALUES(?, ?, ?)", (self.team_id, self.name, self.tag))

@dataclass
class CreateRosterCommand(Command[None]):
    team_id: int
    game: str
    mode: str
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            # get team name and tag
            async with db.execute("SELECT name, tag FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag = row
            # set name and tag to None if they are equal to main team so that they change if the team does
            if self.name == team_name:
                self.name = None
            if self.tag == team_tag:
                self.tag = None
            # check to make sure we aren't making 2 rosters with the same name
            async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ?", (self.team_id, self.game, self.mode, self.name)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    raise Problem('Only one roster per game/mode may use the same name', status=400)
            creation_date = int(datetime.utcnow().timestamp())
            await db.execute("""INSERT INTO team_rosters(team_id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.team_id, self.game, self.mode, self.name, self.tag, creation_date, self.is_recruiting, self.is_active, self.approval_status))
            await db.commit()
            
@dataclass
class EditRosterCommand(Command[None]):
    roster_id: int
    team_id: int
    name: str | None
    tag: str | None
    is_recruiting: bool
    is_active: bool
    approval_status: Approval

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            # get team name and tag
            async with db.execute("SELECT name, tag FROM teams WHERE id = ?", (self.team_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No team found', status=404)
                team_name, team_tag = row
            # set name and tag to None if they are equal to main team so that they change if the team does
            if self.name == team_name:
                self.name = None
            if self.tag == team_tag:
                self.tag = None
            # get the current roster's name and check if it exists
            async with db.execute("SELECT name, game, mode FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem('No roster found')
                roster_name, game, mode = row
            if roster_name != self.name:
                # check to make sure another roster doesn't have the name we're changing to
                async with db.execute("SELECT name FROM team_rosters WHERE team_id = ? AND game = ? AND mode = ? AND name IS ? AND roster_id != ?", (self.team_id, game, mode, self.name, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem('Only one roster per game/mode may use the same name', status=400)
            await db.execute("UPDATE team_rosters SET team_id = ?, name = ?, tag = ?, is_recruiting = ?, is_active = ?, approval_status = ?",
                             (self.team_id, self.name, self.tag, self.is_recruiting, self.is_active, self.approval_status))
            await db.commit()

@dataclass
class InvitePlayerCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id = row[0]
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
            async with db.execute("SELECT id FROM team_members WHERE roster_id = ? AND leave_date IS ?", (self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player is already on this roster", status=404)
            async with db.execute("SELECT COUNT(id) FROM roster_invites WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                num_invites = row[0]
                if num_invites > 0:
                    raise Problem("Player has already been invited", status=400)
            creation_date = int(datetime.utcnow().timestamp())
            await db.execute("INSERT INTO roster_invites(player_id, roster_id, date, is_accepted) VALUES (?, ?, ?, ?)", (self.player_id, self.roster_id, creation_date, False))
            await db.commit()

@dataclass
class DeleteInviteCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id = row[0]
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
            async with db.execute("DELETE FROM roster_invites WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Invite not found")
            await db.commit()

@dataclass
class AcceptInviteCommand(Command[None]):
    invite_id: int
    roster_leave_id: int | None
    player_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT r.game, i.player_id FROM roster_invites i JOIN team_rosters r ON i.roster_id = r.id WHERE i.id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                game, invite_player_id = row
                if self.player_id != invite_player_id:
                    raise Problem("Cannot accept invite for another player", status=400)
            # make sure we have at least one FC for the game of the roster that we are accepting an invite for
            async with db.execute("SELECT count(id) FROM friend_codes WHERE player_id = ? AND game = ?", (self.player_id, game)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                fc_count = row[0]
                if fc_count == 0:
                    raise Problem("Player does not have any friend codes for this roster's game", status=400)
            # we do not move the player to the team's roster just yet, just mark it as accepted, a moderator must approve the transfer
            await db.execute("UPDATE roster_invites SET roster_leave_id = ?, is_accepted = ? WHERE id = ?", (self.roster_leave_id, True, self.invite_id))
            await db.commit()

@dataclass
class DeclineInviteCommand(Command[None]):
    invite_id: int
    player_id: int
    is_privileged: bool = False

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT player_id FROM roster_invites WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                invite_player_id = row[0]
                if self.player_id != invite_player_id and not self.is_privileged:
                    raise Problem("Cannot decline invite for another player", status=400)
            await db.execute("DELETE FROM roster_invites WHERE id = ?", (self.invite_id,))
            await db.commit()

@dataclass
class LeaveRosterCommand(Command[None]):
    player_id: int
    roster_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (self.player_id, self.roster_id, None)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player is not currently on this roster", status=400)
                team_member_id = row[0]
            leave_date = int(datetime.utcnow().timestamp())
            await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (leave_date, team_member_id))

@dataclass
class ApproveTransferCommand(Command[None]):
    invite_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, roster_id, roster_leave_id, is_accepted FROM roster_invites WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Invite not found", status=404)
                player_id, roster_id, roster_leave_id, is_accepted = row
            if not is_accepted:
                raise Problem("Invite has not been accepted by the player yet", status=400)
            if roster_leave_id:
                # check this before we move the player to the new team
                async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ?", (player_id, roster_id, None)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not currently on this roster", status=400)
                    team_member_id = row[0]
            else:
                team_member_id = None
            curr_time = int(datetime.utcnow().timestamp())
            await db.execute("DELETE FROM roster_invites WHERE id = ?", (self.invite_id,))
            await db.execute("INSERT INTO team_members(roster_id, player_id, join_date) VALUES (?, ?, ?)", (roster_id, player_id, curr_time))
            if team_member_id:
                await db.execute("UPDATE team_members SET leave_date = ? WHERE id = ?", (curr_time, team_member_id))