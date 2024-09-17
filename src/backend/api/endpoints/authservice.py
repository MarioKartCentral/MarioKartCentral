from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route
from oauthlib.oauth2 import WebApplicationClient
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from api import settings
from common.auth import pw_hasher
from common.data.commands import *
from common.data.models import *

@dataclass
class LoginRequestData:
    email: str
    password: str

@bind_request_body(LoginRequestData)
async def log_in(request: Request, body: LoginRequestData) -> Response:
    user = await handle(GetUserDataFromEmailCommand(body.email))
    if user is None:
        raise Problem("User not found", status=404)

    is_valid_password = pw_hasher.verify(user.password_hash, body.password)
    if not is_valid_password:
        raise Problem("Invalid login details", status=401)
    
    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    await handle(CreateSessionCommand(session_id, user.id, int(expiration_date.timestamp())))

    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('session', session_id, max_age=int(max_age.total_seconds()))
    return resp

@dataclass
class SignupRequestData:
    email: str
    password: str

@bind_request_body(SignupRequestData)
async def sign_up(request: Request, body: SignupRequestData) -> Response:
    email = body.email # TODO: Email Verification
    password_hash = pw_hasher.hash(body.password)
    user = await handle(CreateUserCommand(email, password_hash))
    await handle(CreateUserSettingsCommand(user.id))
    return JSONResponse(user, status_code=201)

@require_logged_in
async def log_out(request: Request) -> Response:
    session_id = request.state.session_id
    await handle(DeleteSessionCommand(session_id))
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

redirect_uri = 'http://localhost:5000/api/user/discord_callback'

@bind_request_query(LinkDiscordRequestData)
@require_logged_in
async def link_discord(request: Request, data: LinkDiscordRequestData) -> Response:
    client = WebApplicationClient(settings.DISCORD_CLIENT_ID)
    authorization_url = "https://discord.com/oauth2/authorize"
    url = client.prepare_request_uri( # type: ignore
        authorization_url,
        redirect_uri = redirect_uri,
        scope = ['identify guilds'],
        state = data.page_url # store the URL we came from in the state so we can redirect back there after linking
    )
    return RedirectResponse(url, 302) # type: ignore

@bind_request_query(DiscordAuthCallbackData)
@require_logged_in
async def discord_callback(request: Request, data: DiscordAuthCallbackData) -> Response:
    command = LinkUserDiscordCommand(request.state.user.id, data)
    await handle(command)
    # state should contain the URL we were on before linking our discord account,
    # so we should redirect them back there if it exists
    if data.state:
        return RedirectResponse(data.state, 302)
    return JSONResponse({})

@require_logged_in
async def my_discord_data(request: Request) -> Response:
    command = GetUserDiscordCommand(request.state.user.id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_logged_in
async def refresh_discord_data(request: Request) -> JSONResponse:
    command = RefreshUserDiscordDataCommand(request.state.user.id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_logged_in
async def delete_discord_data(request: Request) -> JSONResponse:
    command = DeleteUserDiscordDataCommand(request.state.user.id)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
    Route('/api/user/link_discord', link_discord),
    Route('/api/user/discord_callback', discord_callback),
    Route('/api/user/my_discord', my_discord_data),
    Route('/api/user/refresh_discord', refresh_discord_data, methods=['POST']),
    Route('/api/user/delete_discord', delete_discord_data, methods=['POST'])
]