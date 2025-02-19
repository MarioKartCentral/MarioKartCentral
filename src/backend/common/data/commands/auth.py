from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
from common.auth import permissions
from datetime import datetime, timedelta, timezone
from typing import Iterable
from aiosqlite import Row
import aiohttp
import msgspec
from urllib.parse import urlparse

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
class CheckUserHasPermissionCommand(Command[bool]):
    user_id: int
    permission_name: str
    check_denied_only: bool = False
    team_id: int | None = None
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        series_id = self.series_id

        async with db_wrapper.connect() as db:
            denied_permission_exists = False
            def check_perms(rows: Iterable[Row]):
                num_rows = sum(1 for r in rows) # type: ignore
                if num_rows == 0:
                    # if check_denied_only is True, we only care about the absence of a denied permission,
                    # so an empty result set satisfies that.
                    # if we have previously found a denied permission, we must have a explicitly
                    # approved permission to override it, so don't return true in that case
                    if self.check_denied_only and not denied_permission_exists:
                        return True
                    else:
                        return False
                # if we find an instance of the permission which isnt denied, we have the permission no matter what,
                # so just return True once we find one. otherwise, the permission must have been denied, so we return
                # False after iterating
                for row in rows:
                    is_denied = row[0]
                    if not is_denied:
                        return True
                return False
            
            if self.tournament_id:
                # if tournament is part of a series, we want to find out its id so we can check series permissions also
                if not series_id:
                    async with db.execute("SELECT series_id FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                        row = await cursor.fetchone()
                        if not row:
                            raise Problem("Tournament not found", status=400)
                        series_id = row[0]

                # check tournament roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM tournament_roles r
                    JOIN user_tournament_roles ur ON ur.role_id = r.id
                    JOIN tournament_role_permissions rp ON rp.role_id = r.id
                    JOIN tournament_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.tournament_id = ? AND p.name = ?
                    """, (self.user_id, self.tournament_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()
                perm_check = check_perms(rows)
                # if check_denied_only is false and check_perms returns true,
                # we have the permission, so just return true
                if perm_check and not self.check_denied_only:
                    return True
                # if check_denied_only is true and check_perms returns false,
                # we must have found a denied permission
                if not perm_check and self.check_denied_only:
                    denied_permission_exists = True
                
            if series_id:
                # check series roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM series_roles r
                    JOIN user_series_roles ur ON ur.role_id = r.id
                    JOIN series_role_permissions rp ON rp.role_id = r.id
                    JOIN series_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.series_id = ? AND p.name = ?
                    """, (self.user_id, series_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()

                perm_check = check_perms(rows)
                # if check_denied_only is false and check_perms returns true,
                # we have the permission, so just return true
                if perm_check and not self.check_denied_only:
                    return True
                # if check_denied_only is true and check_perms returns false,
                # we must have found a denied permission
                if not perm_check and self.check_denied_only:
                    denied_permission_exists = True
            
            if self.team_id:
                # check team roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.team_id = ? AND p.name = ?
                    """, (self.user_id, self.team_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()

                perm_check = check_perms(rows)
                # if check_denied_only is false and check_perms returns true,
                # we have the permission, so just return true
                if perm_check and not self.check_denied_only:
                    return True
                # if check_denied_only is true and check_perms returns false,
                # we must have found a denied permission
                if not perm_check and self.check_denied_only:
                    denied_permission_exists = True
            
            #finally, check user roles
            async with db.execute("""
                SELECT DISTINCT rp.is_denied
                FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE ur.user_id = ? AND p.name = ?
                """, (self.user_id, self.permission_name)) as cursor:
                rows = await cursor.fetchall()

            return check_perms(rows)
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])
        
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
class GetModNotificationsCommand(Command[ModNotifications]):
    user_roles: list[UserRole]

    async def handle(self, db_wrapper, s3_wrapper):
        mod_notifications = ModNotifications()
        string_perms: list[str] = []
        for role in self.user_roles:
            for perm in role.permissions:
                string_perms.append(perm.name)

        async with db_wrapper.connect(readonly=True) as db:
            if permissions.MANAGE_TEAMS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM teams WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_teams += row[0]
                # pending roster requests where team is already approved
                async with db.execute("""SELECT COUNT(r.id) FROM team_rosters r JOIN teams t ON r.team_id = t.id 
                                      WHERE t.approval_status='approved' AND r.approval_status='pending'""") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_teams += row[0]
                async with db.execute("SELECT COUNT(id) FROM team_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
                async with db.execute("SELECT COUNT(id) FROM roster_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
            if permissions.MANAGE_TRANSFERS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE is_accepted = 1 AND approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_transfers = row[0]
            if permissions.EDIT_PLAYER in string_perms:
                async with db.execute("SELECT COUNT(id) FROM player_name_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_player_name_changes = row[0]
            if permissions.MANAGE_SHADOW_PLAYERS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM player_claims WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_player_claims = row[0]
        return mod_notifications
    
@dataclass
class LinkUserDiscordCommand(Command[None]):
    user_id: int
    data: DiscordAuthCallbackData
    discord_client_id: str
    discord_client_secret: str
    environment: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        # If we're in a dev environment, we don't want to require everyone to have a client secret just to use the discord functionality.
        # Therefore, just make a fake user so we don't have to make any requests to the Discord API.
        if self.environment == "Development":
            async with db_wrapper.connect() as db:
                await db.execute("DELETE FROM user_discords WHERE user_id = ?", (self.user_id,))
                await db.execute("""INSERT INTO user_discords(user_id, discord_id, username, discriminator, global_name, avatar,
                                    access_token, token_expires_on, refresh_token) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (self.user_id, 0, "test_user", 0,
                                    None, None, "access_token", 0,
                                    "refresh_token"))
                await db.commit()
                return
        # get the base URL to figure out the redirect URI
        base_url = urlparse(self.data.state)._replace(path='', params='', query='').geturl()
        redirect_uri = f'{base_url}/api/user/discord_callback'
        code = self.data.code
        body = {
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": 'authorization_code'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        async with aiohttp.ClientSession() as session:
            base_url = 'https://discord.com/api/v10'
            async with session.post(f'{base_url}/oauth2/token', data=body, headers=headers, auth=aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)) as resp:
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while trying to authenticate: {resp.status}") 
                r = await resp.json()
                token_resp = msgspec.convert(r, type=DiscordAccessTokenResponse)
            headers = {
                'authorization': f'{token_resp.token_type} {token_resp.access_token}'
            }
            async with session.get(f'{base_url}/users/@me', headers=headers) as resp:
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                r = await resp.json()
                discord_user = msgspec.convert(r, type=DiscordUser)
        expires_in = timedelta(seconds=token_resp.expires_in)
        expires_on = int((datetime.now(timezone.utc) + expires_in).timestamp())
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM user_discords WHERE user_id = ?", (self.user_id,))
            await db.execute("""INSERT INTO user_discords(user_id, discord_id, username, discriminator, global_name, avatar,
                                  access_token, token_expires_on, refresh_token) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (self.user_id, discord_user.id, discord_user.username, discord_user.discriminator,
                                   discord_user.global_name, discord_user.avatar, token_resp.access_token, expires_on,
                                   token_resp.refresh_token))
            await db.commit()

@dataclass
class GetUserDiscordCommand(Command[MyDiscordData | None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT discord_id, username, discriminator, global_name, avatar FROM user_discords WHERE user_id = ?",
                                  (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                discord_id, username, discriminator, global_name, avatar = row
                user_discord = MyDiscordData(discord_id, username, discriminator, global_name, avatar, self.user_id)
                return user_discord
            
@dataclass
class RefreshUserDiscordDataCommand(Command[MyDiscordData]):
    user_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT access_token, token_expires_on FROM user_discords WHERE user_id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User does not have a Discord account linked", status=400)
                access_token, token_expires_on = row
            token_expiration = datetime.fromtimestamp(token_expires_on, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            if now >= token_expiration:
                raise Problem("Token is expired, please relink Discord account", status=400)
            headers = {
                'authorization': f'Bearer {access_token}'
            }
            base_url = 'https://discord.com/api/v10'
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{base_url}/users/@me', headers=headers) as resp:
                    if resp.status == 401:
                        raise Problem("Token is expired, please relink Discord account", status=400)
                    if int(resp.status/100) != 2:
                        raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                    r = await resp.json()
                    discord_user = msgspec.convert(r, type=DiscordUser)
                    await db.execute("UPDATE user_discords SET discord_id = ?, username = ?, discriminator = ?, global_name = ?, avatar = ? WHERE user_id = ?",
                                    (discord_user.id, discord_user.username, discord_user.discriminator, discord_user.global_name, discord_user.avatar,
                                     self.user_id))
                    await db.commit()
        return MyDiscordData(discord_user.id, discord_user.username, discord_user.discriminator, discord_user.global_name,
            discord_user.avatar, self.user_id)
    
@dataclass
class DeleteUserDiscordDataCommand(Command[None]):
    user_id: int
    discord_client_id: str
    discord_client_secret: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT access_token, token_expires_on FROM user_discords WHERE user_id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User does not have a Discord account linked", status=400)
                access_token, token_expires_on = row
            token_expiration = datetime.fromtimestamp(token_expires_on, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            if now < token_expiration:
                data: dict[str, str] = {
                    'token': access_token,
                    'token_type_hint': 'access_token'
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                base_url = 'https://discord.com/api/v10'
                async with aiohttp.ClientSession() as session:
                    async with session.post(f'{base_url}/oauth2/token/revoke', data=data, headers=headers, 
                                            auth=aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)) as resp:
                        # 401 means unauthorized which means token is revoked already, so only raise problem if another error occurs
                        if resp.status != 401 and int(resp.status/100) != 2:
                            raise Problem(f"Discord returned an error code: {resp.status}") 
            await db.execute("DELETE FROM user_discords WHERE user_id = ?", (self.user_id,))
            await db.commit()

@dataclass
class RefreshDiscordAccessTokensCommand(Command[None]):
    discord_client_id: str
    discord_client_secret: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            # get all the tokens which expire within a day from now
            # we don't want to get tokens which have already expired since API will return error,
            # just tell user to relink account later
            now = datetime.now(timezone.utc)
            expires_from = int(now.timestamp())
            expires_to = int((now + timedelta(days=1)).timestamp())
            async with db.execute("SELECT user_id, refresh_token FROM user_discords WHERE token_expires_on > ? AND token_expires_on < ?",
                                  (expires_from, expires_to)) as cursor:
                rows = await cursor.fetchall()
        # we execute one big query at the end, so need to store all our parameters in this list
        variable_parameters: list[tuple[str, int, str, int]] = []
        async with aiohttp.ClientSession() as session:
            for row in rows:
                user_id, refresh_token = row
                data: dict[str, str] = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }
                headers: dict[str, str] = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                base_url = 'https://discord.com/api/v10'
                async with session.post(f'{base_url}/oauth2/token', data=data, headers=headers, 
                                        auth=aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)) as resp:
                    # if we don't get a 200 response, just ignore this token and move on to prevent errors
                    if int(resp.status/100) != 2:
                        continue
                    r = await resp.json()
                    token_resp = msgspec.convert(r, type=DiscordAccessTokenResponse)
                    expires_in = timedelta(seconds=token_resp.expires_in)
                    expires_on = int((datetime.now(timezone.utc) + expires_in).timestamp())
                    params = (token_resp.access_token, expires_on, token_resp.refresh_token, user_id)
                    variable_parameters.append(params)
        # use our variable parameters from before to update our database
        if len(variable_parameters):
            async with db_wrapper.connect() as db:
                await db.executemany("UPDATE user_discords SET access_token = ?, token_expires_on = ?, refresh_token = ? WHERE user_id = ?",
                                    variable_parameters)
                await db.commit()