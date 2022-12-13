import sys
sys.path.insert(0, '../constants.py')

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

async def grant_administrator(request: Request) -> JSONResponse:
    if not await current_user_has_permission(request, 'grant_administrator'):
        return JSONResponse({'error':'Unauthorized to grant administrator'}, status_code=401)
    
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
                    return JSONResponse({'error':'User not found with given ID'}, status_code=404)
                else:
                    return JSONResponse({'error':'Unexpected error'}, status_code=500)

    return JSONResponse({}, status_code=200)
