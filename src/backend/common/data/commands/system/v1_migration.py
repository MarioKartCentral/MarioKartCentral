
from dataclasses import dataclass
import msgspec
from common.data.s3 import S3Wrapper, MKCV1_BUCKET
from common.data.db.db_wrapper import DBWrapper
from common.data.models.common import Problem
from common.data.models.mkcv1 import *
from common.data.models.users import UserLoginData
from common.data.commands import Command, save_to_command_log
from common.auth import roles, series_roles, team_roles


@dataclass
class GetMKCV1UserCommand(Command[NewMKCUser | None]):
    email: str

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        user_bytes = await s3_wrapper.get_object(MKCV1_BUCKET, "users.json")
        if user_bytes is None:
            return None # we shouldn't interrupt login flow if this fails
        user_data = msgspec.json.decode(user_bytes, type=NewMKCUserData)
        if self.email.lower() not in user_data.users:
            return None
        v1_user = user_data.users[self.email.lower()]
        # make sure users cant claim an account if the linked player already has an account
        if v1_user.player_id is not None:
            async with db_wrapper.connect(readonly=True) as db:
                async with db.execute("SELECT id FROM users WHERE player_id = ?", (v1_user.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return None
        return v1_user
    
@dataclass
class GetMKCV1UserByPlayerIDCommand(Command[NewMKCUser | None]):
    player_id: int

    async def handle(self, db_wrapper: DBWrapper, s3_wrapper: S3Wrapper):
        # if there's a user with the player id already, just return None
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return None
        user_bytes = await s3_wrapper.get_object(MKCV1_BUCKET, "users_by_player_id.json")
        if user_bytes is None:
            return None
        user_data = msgspec.json.decode(user_bytes, type=NewMKCUserDataByPlayer)
        if self.player_id not in user_data.users:
            return None
        v1_user = user_data.users[self.player_id]
        # make sure users cant transfer an account if they previously transferred their account and changed their email
        if v1_user.player_id is not None:
            async with db_wrapper.connect(readonly=True) as db:
                async with db.execute("SELECT id FROM users WHERE player_id = ?", (v1_user.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return None
        return v1_user

@save_to_command_log
@dataclass
class TransferMKCV1UserCommand(Command[UserLoginData]):
    email: str
    password_hash: str | None
    join_date: int
    player_id: int | None
    about_me: str | None
    user_roles: list[NewMKCUserRole]
    series_roles: list[NewMKCSeriesRole]
    team_roles: list[NewMKCTeamRole]

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"]) as db:
            email_confirmed = True
            force_password_reset = True
            row = await db.execute_insert("INSERT INTO users(join_date, player_id) VALUES(:join_date, :player_id)", 
                                          {"join_date": self.join_date, "player_id": self.player_id})
            if row is None or not row[0]:
                raise Problem("Failed to generate user ID from main table")
            
            user_id = int(row[0])

            insert_query = '''
                INSERT INTO auth.user_auth(user_id, email, password_hash, email_confirmed, force_password_reset)
                VALUES(:user_id, :email, :password_hash, :email_confirmed, :force_password_reset)
            '''
            await db.execute_insert(insert_query, {"user_id": user_id, "email": self.email, "password_hash": self.password_hash,
                                                   "email_confirmed": email_confirmed, "force_password_reset": force_password_reset})

            is_banned = False
            expiration_date: int | None = None
            if self.player_id:
                async with db.execute("SELECT expiration_date FROM player_bans WHERE player_id = ?", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        is_banned = True
                        if row[0]:
                            expiration_date = int(row[0])

            # add about me from old site data
            await db.execute("INSERT INTO user_settings(user_id, about_me) VALUES(?, ?)", (user_id, self.about_me))

            # add user, series, team roles
            insert_user_roles: set[tuple[int, int, int | None]] = set([(user_id, roles.id_by_default_role[role.role_name], None) for role in self.user_roles])
            if is_banned:
                insert_user_roles.add((user_id, roles.id_by_default_role[roles.BANNED], expiration_date))
            insert_series_roles = set([(user_id, series_roles.id_by_default_role[role.role_name], role.series_id) for role in self.series_roles])
            insert_team_roles = set([(user_id, team_roles.id_by_default_role[role.role_name], role.team_id, role.team_id) for role in self.team_roles])
            await db.executemany("""INSERT INTO user_roles(user_id, role_id, expires_on) VALUES(?, ?, ?)""", insert_user_roles)
            await db.executemany("""INSERT INTO user_series_roles(user_id, role_id, series_id) VALUES(?, ?, ?)""", insert_series_roles)
            await db.executemany("""INSERT INTO user_team_roles(user_id, role_id, team_id)
                                    SELECT ?, ?, ?
                                    WHERE EXISTS(SELECT 1 FROM teams WHERE id = ?)""", insert_team_roles)
            await db.commit()
            return UserLoginData(user_id, self.player_id, email_confirmed, force_password_reset, self.email, self.password_hash)