from typing import Awaitable, Callable, Concatenate
from starlette.requests import Request
from starlette.responses import Response
from api.data import handle
from api.utils.responses import ProblemResponse
from common.data.commands import *
from common.data.models import Problem


def require_logged_in[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        session_id = request.cookies.get("session", None)
        if session_id is None:
            raise Problem("Not logged in", status=401)

        user = await handle(GetUserIdFromSessionCommand(session_id))

        if user is not None:
            request.state.session_id = session_id
            request.state.user = user
            return await handle_request(request, *args, **kwargs)
        else:
            resp = ProblemResponse(Problem("Not logged in", status=401))
            resp.delete_cookie("session")
            return resp

    return wrapper

# if check_denied_only is True, as long as the permission is not denied we authorize the request
def require_permission(permission_name: str, check_denied_only: bool = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            session_id = request.cookies.get("session", None)
            if session_id is None:
                raise Problem("Not logged in", status=401)
            
            user = await handle(GetUserIdFromSessionCommand(session_id))
            if user is None:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, permission_name, check_denied_only))
            if user_has_permission:
                request.state.session_id = session_id
                request.state.user = user
                return await handle_request(request, *args, **kwargs)
            else:
                raise Problem("Insufficient permission", f"User does not have required permission \'{permission_name}\'", status=401)
        return wrapper
    return has_permission_decorator

def require_team_permission(permission_name: str, check_denied_only: bool = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            session_id = request.cookies.get("session", None)
            if session_id is None:
                raise Problem("Not logged in", status=401)
            
            user = await handle(GetUserIdFromSessionCommand(session_id))
            if user is None:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            body = await request.json()
            team_id = body.get("team_id", None)

            if team_id is None:
                raise Problem("No team ID specified", status=400)
            
            user_has_permission = await handle(CheckUserHasTeamPermissionCommand(user.id, team_id, permission_name, check_denied_only))

            if user_has_permission:
                request.state.session_id = session_id
                request.state.user = user
                return await handle_request(request, *args, **kwargs)
            else:
                raise Problem("Insufficient permission", f"User does not have required permission \'{permission_name}\'", status=401)
        return wrapper
    return has_permission_decorator