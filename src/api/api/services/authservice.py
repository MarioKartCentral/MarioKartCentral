from datetime import datetime, timedelta, timezone
import secrets
import aiosqlite
from argon2 import PasswordHasher
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.constants import *

hasher = PasswordHasher()

async def login(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"]
    password = body["password"]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, password_hash FROM users WHERE email = ?", (email, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'Invalid login details'}, status_code=401)
            user_id = row[0]
            password_hash = row[1]

    try:
        is_valid_password = hasher.verify(password_hash, password)
        if not is_valid_password:
            return JSONResponse({'error':'Invalid login details'}, status_code=401)
    except:
        return JSONResponse({'error':'Invalid login details'}, status_code=401)

    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)", (session_id, user_id, expiration_date.timestamp()))
        await db.commit()

    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('session', session_id, max_age=int(max_age.total_seconds()))
    return resp

async def sign_up(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"] # TODO: Email Verification
    password_hash = hasher.hash(body["password"])
    async with aiosqlite.connect(DB_PATH) as db:
        user_id = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (email, password_hash))
        await db.commit()
    
    return JSONResponse({'id': user_id, 'email': email}, status_code=201)

async def logout(request: Request) -> JSONResponse:
    session_id = request.cookies.get("session", None)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id, ))
        await db.commit()
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

def get_routes():
    return [
        Route('/api/user/signup', sign_up, methods=["POST"]),
        Route('/api/user/login', login, methods=["POST"]),
        Route('/api/user/logout', logout, methods=["POST"]),
    ]