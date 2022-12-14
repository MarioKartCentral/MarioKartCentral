
import aiosqlite
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.constants import *


async def list_players(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name FROM players") as cursor:
            names = [{'id': row[0], 'name': row[1]} for row in await cursor.fetchall()]
    return JSONResponse({'users': names})


async def list_users(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, email, password_hash FROM users") as cursor:
            names = [{'id': row[0], 'email': row[1], 'password_hash': row[2]} for row in await cursor.fetchall()]
    return JSONResponse({'users': names})


async def current_user(request: Request) -> JSONResponse:
    session_id = request.cookies.get("session", None)
    if session_id is None:
        return JSONResponse({'error': 'Not logged in'}, status_code=401)

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT u.id, u.email, u.password_hash FROM users u JOIN sessions s on s.user_id = u.id WHERE session_id = ?", (session_id, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Not logged in'}, status_code=401)
            user_id = row[0]
            user_email = row[1]
            user_pw_hash = row[2]

        roles_rows = await db.execute_fetchall("SELECT r.name FROM roles r JOIN user_roles ur on ur.role_id = r.id WHERE ur.user_id = ?", (user_id,))
        roles = [row[0] for row in roles_rows]
        return JSONResponse({'id': user_id, 'email': user_email, 'password_hash': user_pw_hash, 'roles': roles})


def get_routes():
    return [
        Route('/api/player/list', list_players),
        Route('/api/user/list', list_users),
        Route('/api/user/me', current_user),
    ]
