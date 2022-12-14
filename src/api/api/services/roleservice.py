import aiosqlite
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import current_user_has_permission
from api.constants import *


async def grant_administrator(request: Request) -> JSONResponse:
    if not await current_user_has_permission(request, 'grant_administrator'):
        return JSONResponse({'error': 'Unauthorized to grant administrator'}, status_code=401)

    body = await request.json()
    user_id = body["user_id"]

    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, 1)", (user_id,))
            await db.commit()
        except Exception as e:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return JSONResponse({'error': 'User not found with given ID'}, status_code=404)
                else:
                    return JSONResponse({'error': 'Unexpected error'}, status_code=500)

    return JSONResponse({}, status_code=200)


def get_routes():
    return [
        Route('/api/user/grant_admin', grant_administrator),
    ]
