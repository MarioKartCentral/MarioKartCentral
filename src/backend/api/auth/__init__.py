from argon2 import PasswordHasher
from starlette.requests import Request
from starlette.responses import JSONResponse
from api.data import handle_command
from common.data.commands import GetUserIdFromSessionCommand, GetUserWithPermissionFromSessionCommand, IsValidSessionCommand


pw_hasher = PasswordHasher()

def require_logged_in(handle_request):
    async def wrapper(request: Request):
        session_id = request.cookies.get("session", None)
        if session_id is None:
            return JSONResponse({'error': 'Not logged in'}, status_code=401)

        user_id = await handle_command(GetUserIdFromSessionCommand(session_id))

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
            
            user_id = await handle_command(GetUserWithPermissionFromSessionCommand(session_id, permission_name))

            if user_id is not None:
                request.state.session_id = session_id
                request.state.user_id = user_id
                return await handle_request(request)
            
            if await handle_command(IsValidSessionCommand(session_id)):
                return JSONResponse({'error': f'User does not have permission \'{permission_name}\''}, status_code=401)
            else:
                resp = JSONResponse({'error': 'Not logged in'}, status_code=401)
                resp.delete_cookie("session")
                return resp
        return wrapper
    return has_permission_decorator