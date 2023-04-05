from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_logged_in
from api.data import connect_db
from api.utils.responses import JSONResponse


async def list_players(request: Request) -> JSONResponse:
    async with connect_db() as db:
        async with db.execute("SELECT id, name FROM players") as cursor:
            names = [{'id': row[0], 'name': row[1]} for row in await cursor.fetchall()]
    return JSONResponse({'users': names})


async def list_users(request: Request) -> JSONResponse:
    async with connect_db() as db:
        async with db.execute("SELECT id, email, password_hash FROM users") as cursor:
            names = [{'id': row[0], 'email': row[1], 'password_hash': row[2]} for row in await cursor.fetchall()]
    return JSONResponse({'users': names})

@require_logged_in
async def current_user(request: Request) -> JSONResponse:
    user_id = request.state.user_id
    async with connect_db() as db:
        async with db.execute("SELECT id, email, password_hash FROM users WHERE id = ?", (user_id, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Unexpected error'}, status_code=500)
            user_id = row[0]
            user_email = row[1]
            user_pw_hash = row[2]

        roles_rows = await db.execute_fetchall("SELECT r.name FROM roles r JOIN user_roles ur on ur.role_id = r.id WHERE ur.user_id = ?", (user_id,))
        roles = [row[0] for row in roles_rows]
        return JSONResponse({'id': user_id, 'email': user_email, 'password_hash': user_pw_hash, 'roles': roles})


routes = [
    Route('/api/player/list', list_players),
    Route('/api/user/list', list_users),
    Route('/api/user/me', current_user),
]
