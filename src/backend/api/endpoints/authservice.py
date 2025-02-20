from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route
from starlette.background import BackgroundTask
from oauthlib.oauth2 import WebApplicationClient
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from api import settings
from common.auth import pw_hasher, permissions
from common.data.commands import *
from common.data.models import *
from urllib.parse import urlparse

@bind_request_body(LoginRequestData)
async def log_in(request: Request, body: LoginRequestData) -> Response:
    user = await handle(GetUserDataFromEmailCommand(body.email))
    if user:
        is_valid_password = pw_hasher.verify(user.password_hash, body.password)
        if not is_valid_password:
            raise Problem("Invalid login details", status=401)
    else:
        # check MKC V1 data for the email/password combo if user can't be found in the database
        mkc_user = await handle(GetMKCV1UserCommand(body.email, body.password))
        password_hash = pw_hasher.hash(body.password)
        if mkc_user is None:
            raise Problem("User not found", status=404)
        # create new user with MKC V1 user's data if it exists
        user = await handle(TransferMKCV1UserCommand(body.email, password_hash, mkc_user.register_date,
                                                     mkc_user.player_id, mkc_user.about_me,
                                                     mkc_user.user_roles, mkc_user.series_roles,
                                                     mkc_user.team_roles))

    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address = request.client.host if request.client else None
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    async def log_ip_fingerprint():
        await handle(LogUserIPCommand(user.id, ip_address))
        await handle(LogFingerprintCommand(body.fingerprint))
        

    resp = JSONResponse({}, status_code=200, background=BackgroundTask(log_ip_fingerprint))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()))
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()))
    return resp

@bind_request_body(SignupRequestData)
async def sign_up(request: Request, body: SignupRequestData) -> Response:
    email = body.email # TODO: Email Verification
    password_hash = pw_hasher.hash(body.password)
    user = await handle(CreateUserCommand(email, password_hash))
    await handle(CreateUserSettingsCommand(user.id))

    # login user after registering
    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address = request.client.host if request.client else None
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    async def log_ip_fingerprint():
        await handle(LogUserIPCommand(user.id, ip_address))
        await handle(LogFingerprintCommand(body.fingerprint))

    resp = JSONResponse(user, status_code=201, background=BackgroundTask(log_ip_fingerprint))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()))
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()))
    return resp

@require_logged_in
async def log_out(request: Request) -> Response:
    session_id = request.state.session_id
    await handle(DeleteSessionCommand(session_id))
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

@bind_request_query(LinkDiscordRequestData)
@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def link_discord(request: Request, data: LinkDiscordRequestData) -> Response:
    client = WebApplicationClient(settings.DISCORD_CLIENT_ID)
    # get the base URL to figure out the redirect URI
    base_url = urlparse(data.page_url)._replace(path='', params='', query='').geturl()
    redirect_uri = f'{base_url}/api/user/discord_callback'
    authorization_url = "https://discord.com/oauth2/authorize"
    url = client.prepare_request_uri( # type: ignore
        authorization_url,
        redirect_uri = redirect_uri,
        scope = ['identify guilds'],
        state = data.page_url # store the URL we came from in the state so we can redirect back there after linking
    )
    return RedirectResponse(url, 302) # type: ignore

@bind_request_query(DiscordAuthCallbackData)
@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def discord_callback(request: Request, data: DiscordAuthCallbackData) -> Response:
    command = LinkUserDiscordCommand(request.state.user.id, data, settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET, settings.ENV)
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

@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def refresh_discord_data(request: Request) -> JSONResponse:
    command = RefreshUserDiscordDataCommand(request.state.user.id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_logged_in
async def delete_discord_data(request: Request) -> JSONResponse:
    command = DeleteUserDiscordDataCommand(request.state.user.id, settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET)
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