from dataclasses import dataclass
from common.data.commands import Command, save_to_command_log
from common.data.models import *
from datetime import datetime, timezone
from typing import Any


@dataclass
class GetUserDataFromEmailCommand(Command[UserLoginData | None]):
    email: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, password_hash, email_confirmed, force_password_reset FROM users WHERE email = ?", (self.email, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                user_id, player_id, password_hash, email_confirmed, force_password_reset = row
            return UserLoginData(user_id, player_id, email_confirmed, force_password_reset, self.email, password_hash)

@dataclass
class GetUserDataFromIdCommand(Command[UserAccountInfo | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, email_confirmed, force_password_reset FROM users WHERE id = ?", (self.id, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            user_id, player_id, email_confirmed, force_password_reset = row
            return UserAccountInfo(user_id, player_id, bool(email_confirmed), bool(force_password_reset))
            
@save_to_command_log     
@dataclass
class CreateUserCommand(Command[UserAccountInfo]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            now = int(datetime.now(timezone.utc).timestamp())
            row = await db.execute_insert("INSERT INTO users(email, password_hash, join_date) VALUES (?, ?, ?)", (self.email, self.password_hash, now))

            # TODO: Run queries to identify why user creation failed
            if row is None:
                raise Problem("Failed to create user")

            await db.commit()
            return UserAccountInfo(int(row[0]), None, False, False)
        
@dataclass
class GetPlayerIdForUserCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> int:
        async with db_wrapper.connect(readonly=True) as db:
            # get player id from user id in request
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("User does not exist", status=404)

                return int(row[0])
            
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
        async with db_wrapper.connect(readonly=True) as db:
            filter = self.filter

            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            limit:int = 50
            offset:int = 0

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            if filter.name_or_email is not None:
                where_clauses.append("(u.email LIKE ? OR p.name LIKE ?)")
                variable_parameters.append(f"%{filter.name_or_email}%")
                variable_parameters.append(f"%{filter.name_or_email}%")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            query = f"""SELECT u.id, u.email, u.join_date, u.email_confirmed, u.force_password_reset,
                p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date
                FROM users u
                LEFT JOIN players p ON u.player_id = p.id
                {where_clause}
                COLLATE NOCASE LIMIT ? OFFSET ?"""
            
            users: list[UserInfo] = []
            async with db.execute(query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    user_id, email, u_join_date, email_confirmed, force_password_reset, player_id, name, country_code, is_hidden, is_shadow, is_banned, p_join_date = row
                    if player_id:
                        player = Player(player_id, name, country_code, is_hidden, is_shadow, is_banned, p_join_date, None)
                    else:
                        player = None
                    user = UserInfo(user_id, email, u_join_date, bool(email_confirmed), bool(force_password_reset), player)
                    users.append(user)

            count_query = f"""SELECT COUNT(*) FROM (
                                    SELECT u.id FROM users u 
                                    LEFT JOIN players p ON u.player_id = p.id
                                    {where_clause})"""
            
            page_count: int = 0
            user_count: int = 0
            async with db.execute(count_query, variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                user_count = row[0]

            page_count = int(user_count / limit) + (1 if user_count % limit else 0)
            return UserList(users, user_count, page_count)
        
@dataclass
class ViewUserCommand(Command[UserInfo]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, email, join_date, email_confirmed, force_password_reset FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                player_id, email, u_join_date, email_confirmed, force_password_reset = row
            player = None
            if player_id:
                async with db.execute("SELECT name, country_code, is_hidden, is_shadow, is_banned, join_date FROM players WHERE id = ?", (player_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    name, country_code, is_hidden, is_shadow, is_banned, p_join_date = row
                discord = None
                async with db.execute("SELECT discord_id, username, discriminator, global_name, avatar FROM user_discords WHERE user_id = ?", (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        discord_id, username, discriminator, global_name, avatar = row
                        discord = Discord(discord_id, username, discriminator, global_name, avatar)
                player = Player(player_id, name, country_code, is_hidden, is_shadow, is_banned, p_join_date, discord)
            return UserInfo(self.user_id, email, u_join_date, bool(email_confirmed), bool(force_password_reset), player)
        
@dataclass
class EditUserCommand(Command[None]):
    mod_user_id: int
    user_id: int
    email: str
    password_hash: str | None
    email_confirmed: bool
    force_password_reset: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
            
            # users should only be able to edit users lower in the role hierarchy
            # than them. editing yourself is an exception, since you are the same level in the
            # role hierarchy as yourself
            if self.mod_user_id != self.user_id:
                async with db.execute("""
                    WITH mod_highest_role AS (
                        SELECT MIN(r.position) AS pos
                        FROM roles r
                        JOIN user_roles ur ON r.id = ur.role_id
                        WHERE ur.user_id = ?
                    ),
                    user_highest_role AS (
                        SELECT MIN(r.position) AS pos
                        FROM roles r
                        JOIN user_roles ur ON r.id = ur.role_id
                        WHERE ur.user_id = ?
                    )
                    SELECT 1
                    FROM mod_highest_role
                    JOIN user_highest_role
                    WHERE user_highest_role.pos IS NULL OR mod_highest_role.pos < user_highest_role.pos
                    """, (self.mod_user_id, self.user_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Cannot edit users higher/equal in the role hierarchy to yourself", status=401)

            async with db.execute("SELECT id FROM users WHERE email = ? AND id != ?", (self.email, self.user_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Another user is already using this email", status=400)
            if self.password_hash:
                await db.execute("UPDATE users SET email = ?, password_hash = ?, email_confirmed = ?, force_password_reset = ? WHERE id = ?", 
                                 (self.email, self.password_hash, self.email_confirmed, self.force_password_reset, self.user_id))
            else:
                await db.execute("UPDATE users SET email = ?, email_confirmed = ?, force_password_reset = ? WHERE id = ?", (self.email, self.email_confirmed, self.force_password_reset, self.user_id))
            await db.commit()