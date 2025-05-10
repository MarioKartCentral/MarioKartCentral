from dataclasses import dataclass
from typing import Dict
from common.data.commands import Command, save_to_command_log
from common.data.models import *
from datetime import datetime, timezone


@dataclass
class GetUserDataFromEmailCommand(Command[UserLoginData | None]):
    email: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"], readonly=True) as db:
            query = '''
                SELECT a.user_id, u.player_id, a.password_hash, a.email_confirmed, a.force_password_reset
                FROM auth.user_auth a
                LEFT JOIN users u ON u.id = a.user_id
                WHERE a.email = :email
            '''
            async with db.execute(query, {"email": self.email}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                user_id, player_id, password_hash, email_conf_int, force_pw_int = row
        return UserLoginData(user_id, player_id, bool(email_conf_int), bool(force_pw_int), self.email, password_hash)

@dataclass
class GetUserDataFromIdCommand(Command[UserAccountInfo | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"], readonly=True) as db:
            query = '''
                SELECT a.email_confirmed, a.force_password_reset, u.player_id
                FROM auth.user_auth a
                LEFT JOIN users u ON u.id = a.user_id
                WHERE a.user_id = :user_id
            '''
            async with db.execute(query, {"user_id": self.id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                email_confirmed, force_password_reset, player_id = row
        return UserAccountInfo(self.id, player_id, bool(email_confirmed), bool(force_password_reset))

@save_to_command_log
@dataclass
class CreateUserCommand(Command[UserAccountInfo]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        now = int(datetime.now(timezone.utc).timestamp())

        async with db_wrapper.connect(db_name='main', attach=["auth"]) as db:
            row = await db.execute_insert("INSERT INTO users(join_date) VALUES(:join_date)", {"join_date": now})
            if row is None or not row[0]:
                raise Problem("Failed to generate user ID from main table")
            user_id = int(row[0])

            insert_query = '''
                INSERT INTO auth.user_auth(user_id, email, password_hash, email_confirmed, force_password_reset)
                VALUES(:user_id, :email, :password_hash, 0, 0)
            '''
            await db.execute_insert(insert_query, {"user_id": user_id, "email": self.email, "password_hash": self.password_hash})
            await db.commit()

        return UserAccountInfo(user_id, None, False, False)

@dataclass
class GetPlayerIdForUserCommand(Command[int | None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> int | None:
        async with db_wrapper.connect(db_name='main', readonly=True) as db:
            async with db.execute("SELECT player_id FROM users WHERE id = :user_id", {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("User does not exist", status=404)

                player_id = row[0]
                return player_id if player_id is not None else None

@dataclass
class GetInvitesForPlayerCommand(Command[PlayerInvites]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> PlayerInvites:
        team_invites: list[TeamInvite] = []
        tournament_invites: list[TournamentInvite] = []
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT i.id, i.date, i.is_bagger_clause, t.id, t.name, t.tag, t.color, r.id, r.name, r.tag, r.game, r.mode
                                    FROM team_transfers i
                                    JOIN team_rosters r ON i.roster_id = r.id
                                    JOIN teams t ON r.team_id = t.id
                                    WHERE i.player_id = ? AND i.is_accepted = 0""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    invite_id, date, is_bagger_clause, team_id, team_name, team_tag, team_color, roster_id, roster_name, roster_tag, game, mode = row
                    roster_name = roster_name if roster_name is not None else team_name
                    roster_tag = roster_tag if roster_tag is not None else team_tag
                    team_invites.append(TeamInvite(invite_id, date, bool(is_bagger_clause), team_id, team_name, team_tag,
                                                   team_color, roster_id, roster_name, roster_tag, game, mode))
            async with db.execute("""SELECT i.id, i.tournament_id, i.timestamp, i.is_bagger_clause, s.name, s.tag, s.color,
                                    t.name, t.game, t.mode
                                    FROM tournament_players i
                                    JOIN tournament_registrations s ON i.registration_id = s.id
                                    JOIN tournaments t ON i.tournament_id = t.id
                                    WHERE i.is_invite = 1 AND i.player_id = ?
                                    AND t.registrations_open = 1""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    tournament_invites.append(TournamentInvite(*row))
        return PlayerInvites(self.player_id, team_invites, tournament_invites)
    
@dataclass
class ListUsersCommand(Command[UserList]):
    filter: UserFilter

    async def handle(self, db_wrapper, s3_wrapper):
        limit: int = 50
        offset: int = 0
        if self.filter.page is not None:
            offset = (self.filter.page - 1) * limit

        async with db_wrapper.connect(db_name='main', attach=["auth"], readonly=True) as db:
            # Single CTE query for paginated users and total count
            query = """
                WITH filtered_users AS (
                    SELECT u.id, u.player_id, u.join_date,
                           a.email, a.email_confirmed, a.force_password_reset,
                           p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date as player_join_date
                    FROM users u
                    JOIN auth.user_auth a ON u.id = a.user_id
                    LEFT JOIN players p ON u.player_id = p.id
                    WHERE (:name_or_email IS NULL OR a.email LIKE '%' || :name_or_email || '%' OR p.name LIKE '%' || :name_or_email || '%')
                )
                SELECT fu.id, fu.player_id, fu.join_date,
                       fu.email, fu.email_confirmed, fu.force_password_reset,
                       fu.name, fu.country_code, fu.is_hidden, fu.is_shadow, fu.is_banned, fu.player_join_date,
                       (SELECT COUNT(*) FROM filtered_users) as total_count
                FROM filtered_users fu
                ORDER BY fu.id
                LIMIT :limit OFFSET :offset
            """
            users: list[UserInfo] = []
            user_count: int = 0
            async with db.execute(query, {"name_or_email": self.filter.name_or_email, "limit": limit, "offset": offset}) as cursor:
                async for row in cursor:
                    (user_id, player_id, join_date, email, email_confirmed_int, force_password_reset_int,
                     player_name, country_code, is_hidden_int, is_shadow_int, is_banned_int, player_join_date,
                     total_count) = row
                    
                    if user_count == 0:
                        user_count = total_count

                    player = None
                    if player_id is not None and player_name:
                        player = Player(player_id, player_name, country_code, bool(is_hidden_int), bool(is_shadow_int), bool(is_banned_int), player_join_date, None)
                    users.append(UserInfo(user_id, email, join_date, bool(email_confirmed_int), bool(force_password_reset_int), player))
        page_count = (user_count + limit - 1) // limit if user_count > 0 else 0
        return UserList(users, user_count, page_count)

@dataclass
class ViewUserCommand(Command[UserInfoDetailed]):
    user_id: int
    mod_user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"], readonly=True) as db:
            query = """
                SELECT u.id, u.player_id, u.join_date,
                       a.email, a.email_confirmed, a.force_password_reset,
                       p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date as pjd,
                       d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                FROM users u
                JOIN auth.user_auth a ON u.id = a.user_id
                LEFT JOIN players p ON u.player_id = p.id
                LEFT JOIN user_discords d ON u.id = d.user_id
                WHERE u.id = :user_id
            """
            async with db.execute(query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                (user_id, player_id, join_date, email, email_confirmed_int, force_password_reset_int, player_name,
                 country_code, is_hidden_int, is_shadow_int, is_banned_int, player_join_date, discord_id,
                 discord_username, discord_discriminator, discord_global_name, discord_avatar) = row
                player = None
                if player_id is not None and player_name:
                    discord = None
                    if discord_id is not None:
                        discord = Discord(discord_id, discord_username, discord_discriminator, discord_global_name, discord_avatar)
                    player = Player(player_id, player_name, country_code, bool(is_hidden_int), bool(is_shadow_int), bool(is_banned_int), player_join_date, discord)

            # admins should only be able to view API tokens for users with lower permissions than themselves (or themselves)
            is_privileged = True
            if self.mod_user_id != self.user_id:
                perm_query = """
                    WITH mh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:mod_user_id),
                         uh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:user_id)
                    SELECT EXISTS(SELECT 1 FROM mh JOIN uh WHERE uh.pos IS NULL OR mh.pos < uh.pos)
                """
                async with db.execute(perm_query, {"mod_user_id": self.mod_user_id, "user_id": self.user_id}) as cursor:
                    row = await cursor.fetchone()
                    if not row or not row[0]:
                        is_privileged = False

            tokens: list[APIToken] = []
            if is_privileged:
                async with db.execute("SELECT token_id, name FROM auth.api_tokens WHERE user_id = ?", (self.user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        token_id, token_name = row
                        tokens.append(APIToken(user_id, token_id, token_name))
                        
            return UserInfoDetailed(user_id, email, join_date, bool(email_confirmed_int), bool(force_password_reset_int), player, tokens)

@dataclass
class EditUserCommand(Command[None]):
    mod_user_id: int
    user_id: int
    email: str
    password_hash: str | None
    email_confirmed: bool
    force_password_reset: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"]) as db:
            exists_query = "SELECT EXISTS(SELECT 1 FROM users WHERE id = :user_id)"
            async with db.execute(exists_query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row or not row[0]:
                    raise Problem("User not found", status=404)
            # users should only be able to edit users lower in the role hierarchy
            # than them. editing yourself is an exception, since you are the same level in the
            # role hierarchy as yourself
            if self.mod_user_id != self.user_id:
                perm_query = """
                    WITH mh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:mod_user_id),
                         uh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:user_id)
                    SELECT EXISTS(SELECT 1 FROM mh JOIN uh WHERE uh.pos IS NULL OR mh.pos < uh.pos)
                """
                async with db.execute(perm_query, {"mod_user_id": self.mod_user_id, "user_id": self.user_id}) as cursor:
                    row = await cursor.fetchone()
                    if not row or not row[0]:
                        raise Problem("Cannot edit users higher/equal in the role hierarchy to yourself", status=403)

            # Email uniqueness check
            email_query = "SELECT EXISTS(SELECT 1 FROM auth.user_auth WHERE email = :email AND user_id != :user_id)"
            async with db.execute(email_query, {"email": self.email, "user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    raise Problem("Another user is already using this email", status=409)

            # Update user_auth with conditional password set conditionally
            update_query = """
                UPDATE auth.user_auth
                SET email = :email,
                    email_confirmed = :email_confirmed,
                    force_password_reset = :force_password_reset,
                    password_hash = CASE WHEN :update_password = 1 THEN :password_hash ELSE password_hash END
                WHERE user_id = :user_id
            """
            params: Dict[str, Any] = {
                "email": self.email,
                "email_confirmed": self.email_confirmed,
                "force_password_reset": self.force_password_reset,
                "update_password": 1 if self.password_hash else 0,
                "password_hash": self.password_hash or "",
                "user_id": self.user_id
            }
            await db.execute(update_query, params)
            await db.commit()