from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import require_logged_in, roles
from api.data import connect_db

@require_logged_in
async def grant_role(request: Request) -> JSONResponse:
    body = await request.json()
    user_id = body["user_id"]
    role = body["role"]

    # For now, the rules about which roles can grant other roles is defined here, but we could move it to  the database
    # in the future.
    if role in [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]:
        allowed_roles = [roles.SUPER_ADMINISTRATOR]
    else:
        allowed_roles = [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]

    allowed_role_ids = [roles.id_by_default_role[role] for role in allowed_roles]

    async with connect_db() as db:
        async with db.execute(f"""
            SELECT EXISTS(
                SELECT 1 FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                WHERE u.id = ? AND r.id IN ({','.join(map(str, allowed_role_ids))})
            )""", (request.state.user_id,)) as cursor:
            row = await cursor.fetchone()
            can_grant = row is not None and bool(row[0])

    if not can_grant:
        return JSONResponse({'error': f'User does not have permission to grant roles'}, status_code=401)

    async with connect_db() as db:
        try:
            async with db.execute("SELECT id FROM roles where name = ?", (role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

            if role_id is None:
                return JSONResponse({'error': 'Role not found with given name'}, status_code=404)

            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            await db.commit()
        except Exception as e:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (user_id,)) as cursor:
                row = await cursor.fetchone()
                user_exists = row is not None

            if not user_exists:
                return JSONResponse({'error': 'User not found with given ID'}, status_code=404)
            else:
                return JSONResponse({'error': 'Unexpected error'}, status_code=500)

    return JSONResponse({}, status_code=200)


routes = [
    Route('/api/user/grant_role', grant_role),
]
