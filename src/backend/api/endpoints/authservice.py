from datetime import datetime, timedelta, timezone
import secrets
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import pw_hasher, require_logged_in
from api.data import handle_command
from common.data.commands import CreateSessionCommand, CreateUserCommand, DeleteSessionCommand, GetUserDataFromEmailCommand

async def log_in(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"]
    password = body["password"]

    user = await handle_command(GetUserDataFromEmailCommand(email))
    if user is None:
        return JSONResponse({'error':'Invalid login details'}, status_code=401)

    try:
        is_valid_password = pw_hasher.verify(user.password_hash, password)
        if not is_valid_password:
            return JSONResponse({'error':'Invalid login details'}, status_code=401)
    except:
        return JSONResponse({'error':'Invalid login details'}, status_code=401)
    
    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    await handle_command(CreateSessionCommand(session_id, user.id, int(expiration_date.timestamp())))

    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('session', session_id, max_age=int(max_age.total_seconds()))
    return resp

async def sign_up(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"] # TODO: Email Verification
    password_hash = pw_hasher.hash(body["password"])
    user_id = await handle_command(CreateUserCommand(email, password_hash))
    return JSONResponse({'id': user_id, 'email': email}, status_code=201)

@require_logged_in
async def log_out(request: Request) -> JSONResponse:
    session_id = request.state.session_id
    await handle_command(DeleteSessionCommand(session_id))
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
]