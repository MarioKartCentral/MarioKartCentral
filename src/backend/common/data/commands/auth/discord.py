from datetime import datetime, timedelta, timezone
import aiohttp
import msgspec
from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
from common.data.s3 import IMAGE_BUCKET

@dataclass
class CreateFakeUserDiscordCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        expires_on = 0
        async with db_wrapper.connect(db_name='main', attach=['discord_tokens']) as db:
            await db.execute("DELETE FROM user_discords WHERE user_id = :user_id", 
                            {"user_id": self.user_id})
            
            insert_query = """
                INSERT INTO user_discords(user_id, discord_id, username, discriminator, global_name, avatar)
                VALUES(:user_id, :discord_id, :username, :discriminator, :global_name, :avatar)
            """
            await db.execute(insert_query, {
                "user_id": self.user_id,
                "discord_id": 0, 
                "username": "test_user", 
                "discriminator": 0, 
                "global_name": None, 
                "avatar": None
            })
            
            await db.execute("DELETE FROM discord_tokens.discord_tokens WHERE user_id = :user_id", 
                           {"user_id": self.user_id})
            
            tokens_query = """
                INSERT INTO discord_tokens.discord_tokens(user_id, access_token, token_expires_on, refresh_token)
                VALUES(:user_id, :access_token, :token_expires_on, :refresh_token)
            """
            await db.execute(tokens_query, {
                "user_id": self.user_id,
                "access_token": "access_token",
                "token_expires_on": expires_on,
                "refresh_token": "refresh_token"
            })
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
        body: dict[str, str | None] = {
            "code": code,
            "redirect_uri": self.discord_oauth_callback,
            "grant_type": 'authorization_code'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        async with aiohttp.ClientSession() as session:
            base_url = 'https://discord.com/api/v10'
            auth = aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)
            async with session.post(f'{base_url}/oauth2/token', data=body, headers=headers, auth=auth) as resp:
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while trying to authenticate: {resp.status}") 
                resp_bytes = await resp.content.read()
                token_resp = msgspec.json.decode(resp_bytes, type=DiscordAccessTokenResponse)
            user_headers = {
                'authorization': f'{token_resp.token_type} {token_resp.access_token}'
            }
            async with session.get(f'{base_url}/users/@me', headers=user_headers) as resp:
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                resp_bytes = await resp.content.read()
                discord_user = msgspec.json.decode(resp_bytes, type=DiscordUser)
        expires_in = timedelta(seconds=token_resp.expires_in)
        expires_on = int((datetime.now(timezone.utc) + expires_in).timestamp())
        
        async with db_wrapper.connect(db_name='main', attach=['discord_tokens']) as db:
            await db.execute("DELETE FROM user_discords WHERE user_id = :user_id", 
                           {"user_id": self.user_id})
            
            profile_query = """
                INSERT INTO user_discords(user_id, discord_id, username, discriminator, global_name, avatar)
                VALUES(:user_id, :discord_id, :username, :discriminator, :global_name, :avatar)
            """
            await db.execute(profile_query, {
                "user_id": self.user_id,
                "discord_id": discord_user.id,
                "username": discord_user.username,
                "discriminator": discord_user.discriminator,
                "global_name": discord_user.global_name,
                "avatar": discord_user.avatar
            })
            
            await db.execute("DELETE FROM discord_tokens.discord_tokens WHERE user_id = :user_id", 
                           {"user_id": self.user_id})
            
            tokens_query = """
                INSERT INTO discord_tokens.discord_tokens(user_id, access_token, token_expires_on, refresh_token) 
                VALUES(:user_id, :access_token, :token_expires_on, :refresh_token)
            """
            await db.execute(tokens_query, {
                "user_id": self.user_id,
                "access_token": token_resp.access_token,
                "token_expires_on": expires_on,
                "refresh_token": token_resp.refresh_token
            })
            
            await db.commit()

@dataclass
class GetUserDiscordCommand(Command[MyDiscordData | None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            query = """
                SELECT discord_id, username, discriminator, global_name, avatar 
                FROM user_discords 
                WHERE user_id = :user_id
            """
            async with db.execute(query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                discord_id, username, discriminator, global_name, avatar = row
                return MyDiscordData(discord_id, username, discriminator, global_name, avatar, self.user_id)
            
@dataclass
class RefreshUserDiscordDataCommand(Command[MyDiscordData]):
    user_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=['discord_tokens'], readonly=True) as db:
            tokens_query = """
                SELECT dt.access_token, dt.token_expires_on 
                FROM discord_tokens.discord_tokens dt
                WHERE dt.user_id = :user_id
            """
            async with db.execute(tokens_query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    account_check = "SELECT 1 FROM user_discords WHERE user_id = :user_id"
                    async with db.execute(account_check, {"user_id": self.user_id}) as check_cursor:
                        if await check_cursor.fetchone():
                            raise Problem("Discord tokens not found, please relink your Discord account", status=400)
                        else:
                            raise Problem("User does not have a Discord account linked", status=400)
                
                access_token, token_expires_on = row
                
        token_expiration = datetime.fromtimestamp(token_expires_on, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        if now >= token_expiration:
            raise Problem("Token is expired, please relink Discord account", status=400)
        
        headers = { 'authorization': f'Bearer {access_token}' }
        base_url = 'https://discord.com/api/v10'
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{base_url}/users/@me', headers=headers) as resp:
                if resp.status == 401:
                    raise Problem("Token is expired, please relink Discord account", status=400)
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                resp_bytes = await resp.content.read()
                discord_user = msgspec.json.decode(resp_bytes, type=DiscordUser)
                
                async with db_wrapper.connect() as db:
                    update_query = """
                        UPDATE user_discords 
                        SET discord_id = :discord_id, 
                            username = :username, 
                            discriminator = :discriminator, 
                            global_name = :global_name, 
                            avatar = :avatar 
                        WHERE user_id = :user_id
                    """
                    params: dict[str, Any] = {
                        "discord_id": discord_user.id,
                        "username": discord_user.username,
                        "discriminator": discord_user.discriminator,
                        "global_name": discord_user.global_name,
                        "avatar": discord_user.avatar,
                        "user_id": self.user_id
                    }
                    await db.execute(update_query, params)
                    await db.commit()
        return MyDiscordData(discord_user.id, discord_user.username, discord_user.discriminator, discord_user.global_name, discord_user.avatar, self.user_id)
    
@dataclass
class DeleteUserDiscordDataCommand(Command[None]):
    user_id: int
    discord_client_id: str
    discord_client_secret: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='discord_tokens', readonly=True) as db:
            tokens_query = """
                SELECT access_token, token_expires_on 
                FROM discord_tokens 
                WHERE user_id = :user_id
            """
            async with db.execute(tokens_query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User does not have a Discord account linked", status=400)
                access_token, token_expires_on = row
        
        # If we have valid tokens, revoke them with Discord
        if access_token:
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
                    auth = aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)
                    async with session.post(f'{base_url}/oauth2/token/revoke', data=data, headers=headers, auth=auth) as resp:
                        # 401 means unauthorized which means token is revoked already
                        if resp.status != 401 and int(resp.status/100) != 2:
                            raise Problem(f"Discord returned an error code: {resp.status}")
        
        async with db_wrapper.connect(db_name='main', attach=['discord_tokens']) as db:
            await db.execute("DELETE FROM user_discords WHERE user_id = :user_id", {"user_id": self.user_id})
            await db.execute("UPDATE user_settings SET avatar = NULL WHERE user_id = :user_id", {"user_id": self.user_id})
            await db.execute("DELETE FROM discord_tokens.discord_tokens WHERE user_id = :user_id", {"user_id": self.user_id})
            await db.commit()

@dataclass
class RefreshDiscordAccessTokensCommand(Command[None]):
    discord_client_id: str
    discord_client_secret: str

    async def handle(self, db_wrapper, s3_wrapper):
        now = datetime.now(timezone.utc)
        from_time = int(now.timestamp())
        to_time = int((now + timedelta(days=1)).timestamp())
        
        tokens_to_refresh = []
        async with db_wrapper.connect(db_name='discord_tokens', readonly=True) as db:
            # get all tokens which expire in the next 24 hours
            # we don't want to get tokens which have already expired since the API will return an error
            # just tell user to relink account later
            query = """
                SELECT user_id, refresh_token 
                FROM discord_tokens 
                WHERE token_expires_on > :from_time AND token_expires_on < :to_time
            """
            async with db.execute(query, {"from_time": from_time, "to_time": to_time}) as cursor:
                tokens_to_refresh = await cursor.fetchall()
        
        refreshed_tokens: list[dict[str, Any]] = []
        
        async with aiohttp.ClientSession() as session:
            for user_id, refresh_token in tokens_to_refresh:
                data: dict[str, str] = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }
                headers: dict[str, str] = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                base_url = 'https://discord.com/api/v10'

                auth = aiohttp.BasicAuth(self.discord_client_id, self.discord_client_secret)                
                async with session.post(f'{base_url}/oauth2/token', data=data, headers=headers, auth=auth) as resp:
                    # If we don't get a 200 response, just ignore this token and move on
                    if int(resp.status/100) != 2:
                        continue
                    resp_bytes = await resp.content.read()
                    token_resp = msgspec.json.decode(resp_bytes, type=DiscordAccessTokenResponse)
                    expires_in = timedelta(seconds=token_resp.expires_in)
                    expires_on = int((datetime.now(timezone.utc) + expires_in).timestamp())
                    
                    refreshed_tokens.append({
                        "access_token": token_resp.access_token,
                        "token_expires_on": expires_on,
                        "refresh_token": token_resp.refresh_token,
                        "user_id": user_id
                    })
        
        if refreshed_tokens:
            async with db_wrapper.connect(db_name='discord_tokens') as db:
                update_query = """
                    UPDATE discord_tokens SET 
                        access_token = :access_token, 
                        token_expires_on = :token_expires_on, 
                        refresh_token = :refresh_token
                    WHERE user_id = :user_id
                """
                await db.executemany(update_query, refreshed_tokens)
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
            
@dataclass
class RemoveDiscordAvatarCommand(Command[None]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                user_id = row[0]
            async with db.execute("SELECT avatar FROM user_settings WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User settings not found", status=404)
                avatar_path: str | None = row[0]
            if avatar_path is None:
                raise Problem("User has no avatar", status=400)
            filename = avatar_path.removeprefix("/img/")
            await s3_wrapper.delete_object(IMAGE_BUCKET, key=filename)
            await db.execute("UPDATE user_settings SET avatar = NULL WHERE user_id = ?", (user_id,))
            await db.execute("UPDATE user_discords SET avatar = NULL WHERE user_id = ?", (user_id,))
            await db.commit()