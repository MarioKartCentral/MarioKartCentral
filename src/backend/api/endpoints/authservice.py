from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import pw_hasher
from common.data.commands import *
from common.data.models import Problem

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

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
]