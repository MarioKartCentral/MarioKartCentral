from argon2 import PasswordHasher
from starlette.requests import Request
from starlette.responses import JSONResponse
from api.data import connect_db


pw_hasher = PasswordHasher()

async def get_user_id_from_session(session_id):
    async with connect_db() as db:
        async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (session_id,)) as cursor:
            row = await cursor.fetchone()
            return None if row is None else int(row[0])

def require_logged_in(handle_request):
    async def wrapper(request: Request):
        session_id = request.cookies.get("session", None)
        if session_id is None:
            return JSONResponse({'error': 'Not logged in'}, status_code=401)

        user_id = await get_user_id_from_session(session_id)

        if user_id is not None:
            request.state.session_id = session_id
            request.state.user_id = user_id
            return await handle_request(request)
        else:
            resp = JSONResponse({'error': 'Not logged in'}, status_code=401)
            resp.delete_cookie("session")
            return resp

    return wrapper

def require_permission(permission_name: str):
    def has_permission_decorator(handle_request):
        async def wrapper(request: Request):
            session_id = request.cookies.get("session", None)
            if session_id is None:
                return JSONResponse({'error': 'Not logged in'}, status_code=401)

            async with connect_db() as db:
                async with db.execute("""
                    SELECT u.id FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    JOIN users u on ur.user_id = u.id
                    JOIN sessions s on s.user_id = u.id
                    JOIN role_permissions rp on rp.role_id = r.id
                    JOIN permissions p on rp.permission_id = p.id
                    WHERE s.session_id = ? AND p.name = ?
                    LIMIT 1""", (session_id, permission_name)) as cursor:
                    row = await cursor.fetchone()
                    user_id = None if row is None else int(row[0])

                if user_id is not None:
                    request.state.session_id = session_id
                    request.state.user_id = user_id
                    return await handle_request(request)

                # Either the session is invalid and needs to be cleared, or the user does not have permission
                async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (session_id,)) as cursor:
                    row = await cursor.fetchone()
                    is_session_valid = row is not None and bool(row[0])

                if is_session_valid:
                    return JSONResponse({'error': f'User does not have permission \'{permission_name}\''}, status_code=401)
                else:
                    resp = JSONResponse({'error': 'Not logged in'}, status_code=401)
                    resp.delete_cookie("session")
                    return resp
        return wrapper
    return has_permission_decorator