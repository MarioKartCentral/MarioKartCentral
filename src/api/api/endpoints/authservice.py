from datetime import datetime, timedelta, timezone
import secrets
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import pw_hasher, require_logged_in
from api.db import connect_db

async def log_in(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"]
    password = body["password"]
    async with connect_db() as db:
        async with db.execute("SELECT id, password_hash FROM users WHERE email = ?", (email, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'Invalid login details'}, status_code=401)
            user_id = row[0]
            password_hash = row[1]

    try:
        is_valid_password = pw_hasher.verify(password_hash, password)
        if not is_valid_password:
            return JSONResponse({'error':'Invalid login details'}, status_code=401)
    except:
        return JSONResponse({'error':'Invalid login details'}, status_code=401)

    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    async with connect_db() as db:
        await db.execute("INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)", (session_id, user_id, expiration_date.timestamp()))
        await db.commit()

        async with db.execute("SELECT language, color_scheme FROM user_settings WHERE user_id = ?", (user_id,)) as cursor:
            settings_row = await cursor.fetchone()

    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('session', session_id, max_age=int(max_age.total_seconds()))

    if settings_row is not None:
        resp.set_cookie('language', settings_row[0])
        resp.set_cookie('color_scheme', settings_row[1])

    return resp

async def sign_up(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"] # TODO: Email Verification
    password_hash = pw_hasher.hash(body["password"])
    async with connect_db() as db:
        user_id_tuple = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (email, password_hash))
        user_id = user_id_tuple[0]
        await db.commit()

        # initialize user settings with default values
        await db.execute("INSERT INTO user_settings(user_id) VALUES (?)", (user_id,))
        await db.commit()
    
    return JSONResponse({'id': user_id, 'email': email}, status_code=201)

@require_logged_in
async def log_out(request: Request) -> JSONResponse:
    session_id = request.state.session_id

    async with connect_db() as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id, ))
        await db.commit()

    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

routes = [
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', log_in, methods=["POST"]),
    Route('/api/user/logout', log_out, methods=["POST"]),
]