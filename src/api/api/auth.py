import aiosqlite
from starlette.requests import Request
from api.constants import *


async def current_user_has_permission(request: Request, permission_name: str):
    session_id = request.cookies.get("session", None)
    if session_id is None:
        return False

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT EXISTS(
                SELECT 1 FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                JOIN sessions s on s.user_id = u.id
                JOIN role_permissions rp on rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ?
            )""", (session_id, permission_name)) as cursor:
            row = await cursor.fetchone()
            return row is not None and bool(row[0])
