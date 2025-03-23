from datetime import timedelta, timezone
import aiohttp
import msgspec
from common.data.commands import Command
from common.data.models import *
from common.data.s3 import IMAGE_BUCKET

@dataclass
class CreateFakeUserDiscordCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM user_discords WHERE user_id = ?", (self.user_id,))
            await db.execute("""INSERT INTO user_discords(user_id, discord_id, username, discriminator, global_name, avatar,
                                access_token, token_expires_on, refresh_token) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (self.user_id, 0, "test_user", 0,
                                None, None, "access_token", 0,
                                "refresh_token"))
            await db.commit()

@dataclass
class LinkUserDiscordCommand(Command[None]):
    user_id: int
    data: DiscordAuthCallbackData
    discord_client_id: str
    discord_client_secret: str
    enable: str | None
    discord_oauth_callback: str

    async def handle(self, db_wrapper, s3_wrapper):
        code = self.data.code
        body = {
            "code": code,
            "redirect_uri": self.discord_oauth_callback,  # Use the full redirect URI directly
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
                resp_bytes = await resp.content.read()
                token_resp = msgspec.json.decode(resp_bytes, type=DiscordAccessTokenResponse)
            headers = {
                'authorization': f'{token_resp.token_type} {token_resp.access_token}'
            }
            async with session.get(f'{base_url}/users/@me', headers=headers) as resp:
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                resp_bytes = await resp.content.read()
                discord_user = msgspec.json.decode(resp_bytes, type=DiscordUser)
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
                    resp_bytes = await resp.content.read()
                    discord_user = msgspec.json.decode(resp_bytes, type=DiscordUser)
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
                    resp_bytes = await resp.content.read()
                    token_resp = msgspec.json.decode(resp_bytes, type=DiscordAccessTokenResponse)
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

@dataclass
class SyncDiscordAvatarCommand(Command[str | None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT discord_id, avatar FROM user_discords WHERE user_id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User does not have a Discord account linked", status=400)
                discord_id, avatar = row
                if not avatar:
                    return None

                # Construct Discord CDN URL
                avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png?size=256"
                
                # Download avatar from Discord
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status != 200:
                            raise Problem(f"Failed to fetch Discord avatar: {resp.status}")
                        image_data = await resp.read()

                # Upload to S3
                filename = f"avatars/{discord_id}_{avatar}.png"
                await s3_wrapper.put_object(
                    bucket_name=IMAGE_BUCKET, 
                    key=filename, 
                    body=image_data,
                    acl="public-read"
                )
                
                # Update user settings with new avatar URL including /img/ prefix
                avatar_path = f"/img/{filename}"
                await db.execute(
                    "UPDATE user_settings SET avatar = ? WHERE user_id = ?",
                    (avatar_path, self.user_id)
                )
                await db.commit()
                return avatar_path