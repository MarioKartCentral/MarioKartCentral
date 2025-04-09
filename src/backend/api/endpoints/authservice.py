import traceback
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

# Email configuration helper
def create_email_config():
    email_config = EmailServiceConfig(
        from_email=appsettings.MKC_EMAIL_ADDRESS,
        site_url=appsettings.SITE_URL,
        use_ses=appsettings.USE_SES_FOR_EMAILS
    )
    
    if appsettings.USE_SES_FOR_EMAILS:
        if not appsettings.AWS_SES_ACCESS_KEY or not appsettings.AWS_SES_SECRET_KEY:
            raise Problem("AWS SES access key and secret key must be set if SES is used", status=500)
        email_config.ses_config = SESConfig(
            access_key_id=appsettings.AWS_SES_ACCESS_KEY,
            secret_access_key=str(appsettings.AWS_SES_SECRET_KEY),
            region=appsettings.AWS_SES_REGION
        )
    else:
        email_config.smtp_config = SMTPConfig(hostname=appsettings.MKC_EMAIL_HOSTNAME, port=appsettings.MKC_EMAIL_PORT)
    
    return email_config

@bind_request_body(LoginRequestData)
async def log_in(request: Request, body: LoginRequestData) -> Response:
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
            email_config = create_email_config()
            command = SendPasswordResetEmailCommand(body.email, email_config)
            await handle(command)   
        return JSONResponse(return_user, background=BackgroundTask(send_password_reset))
    
    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address = request.headers.get('CF-Connecting-IP', None) # use cloudflare headers if exists
    if not ip_address:
        ip_address = request.client.host if request.client else None
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    async def log_ip_fingerprint():
        if appsettings.ENABLE_IP_LOGGING:
            await handle(LogUserIPCommand(user.id, ip_address))
        await handle(LogFingerprintCommand(body.fingerprint))
        
    resp = JSONResponse(return_user, status_code=200, background=BackgroundTask(log_ip_fingerprint))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()), secure=True, httponly=True)
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()), secure=True, httponly=True)
    return resp

@bind_request_body(SignupRequestData)
async def sign_up(request: Request, body: SignupRequestData) -> Response:
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
            email_config = create_email_config()
            command = SendPasswordResetEmailCommand(body.email, email_config)
            await handle(command)   
        return JSONResponse(return_user, background=BackgroundTask(send_password_reset))
        
    user = await handle(CreateUserCommand(email, password_hash))
    await handle(CreateUserSettingsCommand(user.id))

    # login user after registering
    persistent_session_id = request.cookies.get('persistentSession', None)
    ip_address = request.headers.get('CF-Connecting-IP', None) # use cloudflare headers if exists
    if not ip_address:
        ip_address = request.client.host if request.client else None
    session = await handle(CreateSessionCommand(user.id, ip_address, persistent_session_id, body.fingerprint))

    # in the background after the response is sent, send a confirmation email and log user IP/fingerprint
    async def send_email_and_log():
        email_config = create_email_config()
        command = SendEmailVerificationCommand(user.id, email_config)
        await handle(command)
        
        if appsettings.ENABLE_IP_LOGGING:
            await handle(LogUserIPCommand(user.id, ip_address))
        await handle(LogFingerprintCommand(body.fingerprint))

    resp = JSONResponse(user, status_code=201, background=BackgroundTask(send_email_and_log))
    resp.set_cookie('session', session.session_id, max_age=int(session.max_age.total_seconds()), secure=True, httponly=True)
    if not persistent_session_id:
        resp.set_cookie('persistentSession', session.persistent_session_id, max_age=int(session.max_age.total_seconds()), secure=True, httponly=True)
    return resp

@require_logged_in
async def log_out(request: Request) -> Response:
    session_id = request.state.session_id
    await handle(DeleteSessionCommand(session_id))
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

@require_logged_in
async def send_confirmation_email(request: Request) -> Response:
    email_config = create_email_config()
    command = SendEmailVerificationCommand(request.state.user.id, email_config)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ConfirmEmailRequestData)
async def confirm_email(request: Request, body: ConfirmEmailRequestData) -> JSONResponse:
    command = VerifyEmailCommand(body.token_id)
    await handle(command)
    return JSONResponse({})

@bind_request_body(ForgotPasswordRequestData)
async def forgot_password(request: Request, body: ForgotPasswordRequestData) -> JSONResponse:
    email_config = create_email_config()
    command = SendPasswordResetEmailCommand(body.email, email_config)
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
@require_logged_in
async def reset_password(request: Request, body: ResetPasswordRequestData):
    new_pw_hash = pw_hasher.hash(body.new_password)
    command = ResetPasswordCommand(request.state.user.id, body.old_password, new_pw_hash)
    await handle(command)
    return JSONResponse({})

@bind_request_body(TransferAccountRequestData)
async def transfer_account(request: Request, body: TransferAccountRequestData):
    command = GetMKCV1UserByPlayerIDCommand(body.player_id)
    mkc_user = await handle(command)
    if not mkc_user:
        raise Problem("Old site account not found", status=404)
    user = await handle(TransferMKCV1UserCommand(mkc_user.email, None, mkc_user.register_date,
        mkc_user.player_id, mkc_user.about_me,
        mkc_user.user_roles, mkc_user.series_roles,
        mkc_user.team_roles))
    async def send_password_reset():
        email_config = create_email_config()
        command = SendPasswordResetEmailCommand(user.email, email_config)
        await handle(command)
    return JSONResponse({}, background=BackgroundTask(send_password_reset))

@bind_request_body(ChangeEmailRequestData)
@require_logged_in
async def change_email(request: Request, body: ChangeEmailRequestData):
    command = ChangeEmailCommand(request.state.user.id, body.new_email, body.password)
    await handle(command)

    async def send_confirmation_email():
        email_config = create_email_config()
        command = SendEmailVerificationCommand(request.state.user.id, email_config)
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
    try:
        if appsettings.ENABLE_DISCORD:
            command = LinkUserDiscordCommand(
                user_data.id, 
                discord_auth_data, 
                appsettings.DISCORD_CLIENT_ID, 
                str(appsettings.DISCORD_CLIENT_SECRET), 
                appsettings.ENV,
                appsettings.DISCORD_OAUTH_CALLBACK 
            )
        else:
            command = CreateFakeUserDiscordCommand(user_data.id)
        await handle(command)
            
    except Exception as e:
        if isinstance(e, Problem):
            print(f"Problem raised during Discord auth callback: {e}")
        traceback.print_exc()
        redirect_params = "?auth_failed=1"

    # If they have not completed registration yet, redirect to registration page, otherwise edit profile page
    if not request.state.user.player_id:
        redirect_path = "/user/player-signup"
    else:
        redirect_path = "/registry/players/edit-profile"

    async def sync_avatar():
        if appsettings.ENABLE_DISCORD:
            command = SyncDiscordAvatarCommand(request.state.user.id)
            await handle(command)

    return RedirectResponse(f"{redirect_path}{redirect_params}", 302, background=BackgroundTask(sync_avatar))

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
    command = DeleteUserDiscordDataCommand(request.state.user.id, appsettings.DISCORD_CLIENT_ID, str(appsettings.DISCORD_CLIENT_SECRET))
    await handle(command)
    return JSONResponse({})

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

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
    Route('/api/user/send_confirmation_email', send_confirmation_email, methods=["POST"]),
    Route('/api/user/confirm_email', confirm_email, methods=["POST"]),
    Route('/api/user/forgot_password', forgot_password, methods=["POST"]),
    Route('/api/user/check_password_token', check_password_reset_token, methods=["POST"]),
    Route('/api/user/reset_password_token', reset_password_with_token, methods=["POST"]),
    Route('/api/user/reset_password', reset_password, methods=["POST"]),
    Route('/api/user/transfer_account', transfer_account, methods=["POST"]),
    Route('/api/user/change_email', change_email, methods=["POST"]),
    Route('/api/user/link_discord', link_discord),
    Route('/api/user/discord_callback', discord_callback),
    Route('/api/user/my_discord', my_discord_data),
    Route('/api/user/refresh_discord', refresh_discord_data, methods=['POST']),
    Route('/api/user/delete_discord', delete_discord_data, methods=['POST']),
    Route('/api/user/sync_discord_avatar', sync_discord_avatar, methods=['POST']),
    Route('/api/user/delete_discord_avatar', delete_discord_avatar, methods=["POST"]),
]