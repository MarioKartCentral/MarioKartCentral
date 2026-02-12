import logging
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from api import appsettings
from common.auth import pw_hasher, permissions
from common.data.commands import *
from common.data.models import *
from urllib.parse import urlencode


@bind_request_body(LoginRequestData)
async def log_in(request: Request, body: LoginRequestData) -> Response:
    time = datetime.now(timezone.utc)
    user = await handle(GetUserDataFromEmailCommand(body.email))
    if user:
        if user.password_hash is None:
            raise Problem("Invalid login details", status=401)
        try:
            pw_hasher.verify(user.password_hash, body.password)
        except:
            raise Problem("Invalid login details", status=401)
    else:
        # check MKC V1 data for the email/password combo if user can't be found in the database
        mkc_user = await handle(GetMKCV1UserCommand(body.email))
        password_hash = pw_hasher.hash(body.password)
        if mkc_user is None:
            raise Problem("User not found", status=404)
        # create new user with MKC V1 user's data if it exists
        user = await handle(TransferMKCV1UserCommand(body.email, password_hash, mkc_user.register_date,
                                                     mkc_user.player_id, mkc_user.about_me,
                                                     mkc_user.user_roles, mkc_user.series_roles,
                                                     mkc_user.team_roles))

    return_user = UserAccountInfo(user.id, user.player_id, user.email_confirmed, user.force_password_reset)

    # if the user is forced to reset their password, send them a password reset email but don't log them in.
    # return info about the user so the frontend can know what's going on
    if user.force_password_reset:
        async def send_password_reset():
            command = SendPasswordResetEmailCommand(body.email)
            await handle(command)   
        return JSONResponse(return_user, background=BackgroundTask(send_password_reset))
    
    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address: str | None = request.state.ip_address
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    async def log_ip_fingerprint():
        if appsettings.ENABLE_IP_LOGGING:
            referer = request.headers.get('Referer', None)
            await handle(EnqueueUserActivityCommand(user.id, ip_address, request.url.path, time, referer))
        await handle(LogFingerprintCommand(body.fingerprint))
        
    resp = JSONResponse(return_user, status_code=200, background=BackgroundTask(log_ip_fingerprint))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()), secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()), secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)
    return resp

@bind_request_body(SignupRequestData)
async def sign_up(request: Request, body: SignupRequestData) -> Response:
    time = datetime.now(timezone.utc)
    existing_user = await handle(GetUserDataFromEmailCommand(body.email))
    if existing_user:
        raise Problem("User with this email already exists", status=400)
    email = body.email # TODO: Email Verification
    password_hash = pw_hasher.hash(body.password)
    # if this is a user from the old MKC site trying to create a new account,
    # import all the data from their old MKC account, and send them a password
    # reset email. don't log them in until their password is reset, just return the user info.
    # the frontend will take care of telling them to reset their password from the response json
    mkc_user = await handle(GetMKCV1UserCommand(body.email))
    if mkc_user:
        user = await handle(TransferMKCV1UserCommand(body.email, password_hash, mkc_user.register_date,
                                                mkc_user.player_id, mkc_user.about_me,
                                                mkc_user.user_roles, mkc_user.series_roles,
                                                mkc_user.team_roles))
        return_user = UserAccountInfo(user.id, user.player_id, user.email_confirmed, user.force_password_reset)
        async def send_password_reset():
            command = SendPasswordResetEmailCommand(body.email)
            await handle(command)   
        return JSONResponse(return_user, background=BackgroundTask(send_password_reset))
        
    user = await handle(CreateUserCommand(email, password_hash))
    await handle(CreateUserSettingsCommand(user.id))

    # login user after registering
    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address: str | None = request.state.ip_address
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    # in the background after the response is sent, send a confirmation email and log user IP/fingerprint
    async def send_email_and_log():
        command = SendEmailVerificationCommand(user.id)
        await handle(command)
        
        if appsettings.ENABLE_IP_LOGGING:
            referer = request.headers.get('Referer', None)
            await handle(EnqueueUserActivityCommand(user.id, ip_address, request.url.path, time, referer))
        await handle(LogFingerprintCommand(body.fingerprint))

    resp = JSONResponse(user, status_code=201, background=BackgroundTask(send_email_and_log))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()), secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()), secure=appsettings.SECURE_HTTP_COOKIES, httponly=True)
    return resp

@require_logged_in(session_only=True)
async def log_out(request: Request) -> Response:
    session_id = request.state.session_id
    await handle(DeleteSessionCommand(session_id))
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

@require_logged_in()
async def send_confirmation_email(request: Request) -> Response:
    command = SendEmailVerificationCommand(request.state.user.id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ConfirmEmailRequestData)
async def confirm_email(request: Request, body: ConfirmEmailRequestData) -> JSONResponse:
    command = VerifyEmailCommand(body.token_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ForgotPasswordRequestData)
async def forgot_password(request: Request, body: ForgotPasswordRequestData) -> JSONResponse:
    command = SendPasswordResetEmailCommand(body.email)
    await handle(command)
    return JSONResponse({})

@bind_request_body(SendPlayerPasswordResetRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def send_player_password_reset(request: Request, body: SendPlayerPasswordResetRequestData) -> JSONResponse:
    command = SendPasswordResetToPlayerCommand(body.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(CheckPasswordTokenRequestData)
async def check_password_reset_token(request: Request, body: CheckPasswordTokenRequestData) -> JSONResponse:
    user_info = await handle(GetUserInfoFromPasswordResetTokenCommand(body.token_id))
    return JSONResponse(user_info)

@bind_request_body(ResetPasswordTokenRequestData)
async def reset_password_with_token(request: Request, body: ResetPasswordTokenRequestData) -> JSONResponse:
    new_password_hash = pw_hasher.hash(body.new_password)
    command = ResetPasswordWithTokenCommand(body.token_id, new_password_hash)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ResetPasswordRequestData)
@require_logged_in()
async def reset_password(request: Request, body: ResetPasswordRequestData):
    new_pw_hash = pw_hasher.hash(body.new_password)
    command = ResetPasswordCommand(request.state.user.id, body.old_password, new_pw_hash)
    await handle(command)
    return JSONResponse({})

@bind_request_body(TransferAccountRequestData)
async def transfer_account(request: Request, body: TransferAccountRequestData):
    existing_user_id = await handle(GetUserIdFromPlayerIdCommand(body.player_id))
    if existing_user_id is not None:
        raise Problem("Your account has already been transferred to the new site, check the email associated with your account for a password reset", status=400)
    command = GetMKCV1UserByPlayerIDCommand(body.player_id)
    mkc_user = await handle(command)
    if not mkc_user:
        raise Problem("Old site account not found", status=404)
    user = await handle(TransferMKCV1UserCommand(mkc_user.email, None, mkc_user.register_date,
        mkc_user.player_id, mkc_user.about_me,
        mkc_user.user_roles, mkc_user.series_roles,
        mkc_user.team_roles))
    async def send_password_reset():
        command = SendPasswordResetEmailCommand(user.email)
        await handle(command)
    return JSONResponse({}, background=BackgroundTask(send_password_reset))

@bind_request_body(ChangeEmailRequestData)
@require_logged_in()
async def change_email(request: Request, body: ChangeEmailRequestData):
    command = ChangeEmailCommand(request.state.user.id, body.new_email, body.password)
    await handle(command)

    async def send_confirmation_email():
        command = SendEmailVerificationCommand(request.state.user.id)
        await handle(command)
    return JSONResponse({}, background=BackgroundTask(send_confirmation_email))

@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def link_discord(request: Request) -> Response:
    params = {
        'client_id': appsettings.DISCORD_CLIENT_ID,
        'redirect_uri': appsettings.DISCORD_OAUTH_CALLBACK,
        'response_type': 'code',
        'scope': 'identify guilds'
    }
    query_string = urlencode(params)
    url = f"https://discord.com/oauth2/authorize?{query_string}"
    return RedirectResponse(url, 302)

@bind_request_query(DiscordAuthCallbackData)
@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def discord_callback(request: Request, discord_auth_data: DiscordAuthCallbackData) -> Response:
    redirect_params = ""
    user_data = request.state.user
    # If they have not completed registration yet, redirect to registration page, otherwise edit profile page
    if not request.state.user.player_id:
        redirect_path = "/user/player-signup"
    else:
        redirect_path = "/registry/players/edit-profile"
    if discord_auth_data.error:
        return RedirectResponse(f"{redirect_path}{redirect_params}", 302)
    assert discord_auth_data.code is not None
    try:
        if appsettings.ENABLE_DISCORD:
            command = LinkUserDiscordCommand(user_data.id, discord_auth_data)
        else:
            command = CreateFakeUserDiscordCommand(user_data.id)
        await handle(command)
            
    except Exception:
        logging.error("Unexpected error occurred during Discord auth callback", exc_info=True)
        redirect_params = "?auth_failed=1"

    async def sync_avatar():
        if appsettings.ENABLE_DISCORD:
            command = SyncDiscordAvatarCommand(request.state.user.id)
            await handle(command)

    return RedirectResponse(f"{redirect_path}{redirect_params}", 302, background=BackgroundTask(sync_avatar))

@require_logged_in()
async def my_discord_data(request: Request) -> Response:
    command = GetUserDiscordCommand(request.state.user.id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_permission(permissions.EDIT_USER)
async def get_discord_data(request: Request) -> Response:
    user_id = request.path_params['user_id']
    command = GetUserDiscordCommand(user_id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def refresh_discord_data(request: Request) -> JSONResponse:
    command = RefreshUserDiscordDataCommand(request.state.user.id)
    discord_data = await handle(command)
    return JSONResponse(discord_data)

@require_logged_in()
async def delete_discord_data(request: Request) -> JSONResponse:
    command = DeleteUserDiscordDataCommand(request.state.user.id)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.EDIT_USER)
async def force_delete_discord_data(request: Request) -> Response:
    user_id = request.path_params['user_id']
    command = DeleteUserDiscordDataCommand(user_id)
    await handle(command)
    return Response(status_code=204)

@require_permission(permissions.LINK_DISCORD, check_denied_only=True)
async def sync_discord_avatar(request: Request) -> JSONResponse:
    command = SyncDiscordAvatarCommand(request.state.user.id)
    avatar_path = await handle(command)
    return JSONResponse({"avatar": avatar_path})

@bind_request_body(RemovePlayerAvatarRequestData)
@require_permission(permissions.EDIT_PLAYER)
async def delete_discord_avatar(request: Request, body: RemovePlayerAvatarRequestData) -> JSONResponse:
    command = RemoveDiscordAvatarCommand(body.player_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(CreateAPITokenRequestData)
@require_permission(permissions.MANAGE_API_TOKENS, session_only=True)
async def create_api_token(request: Request, body: CreateAPITokenRequestData) -> JSONResponse:
    user_id = request.path_params['user_id']
    command = CreateAPITokenCommand(user_id, request.state.user.id, body.name)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.MANAGE_API_TOKENS, session_only=True)
async def user_api_tokens(request: Request) -> JSONResponse:
    user_id = request.path_params['user_id']
    command = GetUserAPITokensCommand(int(user_id))
    tokens = await handle(command)
    return JSONResponse(tokens)

@require_logged_in(session_only=True)
async def my_api_tokens(request: Request) -> JSONResponse:
    command = GetUserAPITokensCommand(request.state.user.id)
    tokens = await handle(command)
    return JSONResponse(tokens)

@bind_request_body(DeleteAPITokenRequestData)
@require_permission(permissions.MANAGE_API_TOKENS, session_only=True)
async def mod_delete_api_token(request: Request, body: DeleteAPITokenRequestData) -> JSONResponse:
    user_id = request.path_params['user_id']
    command = DeleteAPITokenCommand(body.token_id, user_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(DeleteAPITokenRequestData)
@require_logged_in(session_only=True)
async def delete_api_token(request: Request, body: DeleteAPITokenRequestData) -> JSONResponse:
    user_id = request.state.user.id
    command = DeleteAPITokenCommand(body.token_id, user_id)
    await handle(command)
    return JSONResponse({})

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
    Route('/api/user/send_confirmation_email', send_confirmation_email, methods=["POST"]),
    Route('/api/user/confirm_email', confirm_email, methods=["POST"]),
    Route('/api/user/forgot_password', forgot_password, methods=["POST"]),
    Route('/api/user/send_player_password_reset', send_player_password_reset, methods=['POST']),
    Route('/api/user/check_password_token', check_password_reset_token, methods=["POST"]),
    Route('/api/user/reset_password_token', reset_password_with_token, methods=["POST"]),
    Route('/api/user/reset_password', reset_password, methods=["POST"]),
    Route('/api/user/transfer_account', transfer_account, methods=["POST"]),
    Route('/api/user/change_email', change_email, methods=["POST"]),
    Route('/api/user/link_discord', link_discord),
    Route('/api/user/discord_callback', discord_callback),
    Route('/api/user/my_discord', my_discord_data),
    Route('/api/user/{user_id:int}/discord', get_discord_data),
    Route('/api/user/refresh_discord', refresh_discord_data, methods=['POST']),
    Route('/api/user/delete_discord', delete_discord_data, methods=['POST']),
    Route('/api/user/{user_id:int}/discord/forceDelete', force_delete_discord_data, methods=['POST']),
    Route('/api/user/sync_discord_avatar', sync_discord_avatar, methods=['POST']),
    Route('/api/user/delete_discord_avatar', delete_discord_avatar, methods=["POST"]),
    Route('/api/user/{user_id:int}/create_api_token', create_api_token, methods=["POST"]),
    Route('/api/user/{user_id:int}/user_api_tokens', user_api_tokens),
    Route('/api/user/{user_id:int}/delete_api_token', mod_delete_api_token, methods=["POST"]),
    Route('/api/user/api_tokens', my_api_tokens),
    Route('/api/user/delete_api_token', delete_api_token, methods=["POST"]),
]