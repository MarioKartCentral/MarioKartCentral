from typing import Any
import aiohttp
import msgspec

from common.data.models.common import Problem
from common.data.models.discord_integration import DiscordAccessTokenResponse, DiscordAuthCallbackData, DiscordUser

class DiscordApi:
    def __init__(self, discord_client_id: str, discord_client_secret: str, redirect_uri: str | None = None):
        self.discord_client_id = discord_client_id
        self.discord_client_secret = discord_client_secret
        self.redirect_uri = redirect_uri

    async def handle_auth_callback(self, data: DiscordAuthCallbackData):
        if not self.redirect_uri:
            raise Problem("Discord OAuth is not configured", status=500)
        body: dict[str, Any] = {
            "code": data.code,
            "redirect_uri": self.redirect_uri,
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

        return token_resp, discord_user
    
    async def get_user(self, access_token: str) -> DiscordUser:
        headers = { 'authorization': f'Bearer {access_token}' }
        base_url = 'https://discord.com/api/v10'
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{base_url}/users/@me', headers=headers) as resp:
                if resp.status == 401:
                    raise Problem("Token is expired, please relink Discord account", status=400)
                if int(resp.status/100) != 2:
                    raise Problem(f"Discord returned an error code while fetching user data: {resp.status}") 
                resp_bytes = await resp.content.read()
                return msgspec.json.decode(resp_bytes, type=DiscordUser)
            
    async def refresh_token(self, refresh_token: str):
        async with aiohttp.ClientSession() as session:
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
                    return None
                resp_bytes = await resp.content.read()
                return msgspec.json.decode(resp_bytes, type=DiscordAccessTokenResponse)
            
    async def revoke_token(self, access_token: str):
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
    
    async def get_avatar(self, discord_id: str, avatar: str) -> bytes:
        avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png?size=256"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status != 200:
                    raise Problem(f"Failed to fetch Discord avatar: {resp.status}")
                return await resp.read()