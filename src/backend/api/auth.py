from typing import Awaitable, Callable, Concatenate
from starlette.requests import Request
from starlette.responses import Response
from api.data import handle
from api.utils.responses import ProblemResponse
from common.data.commands import *
from common.data.models import Problem, User
from common.auth import permissions, series_permissions, tournament_permissions

# returns user and session ID
# session_only: only use cookies and not authorization header
async def get_user(request: Request, session_only=False) -> tuple[User | None, str | None]:
    session_id = request.cookies.get("session", None)
    if session_id:
        user = await handle(GetUserIdFromSessionCommand(session_id))
    elif session_only:
        return None, None
    else:
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return None, None
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise Problem("Invalid Authorization header", status=401)
        user = await handle(GetUserFromAPITokenCommand(token))
    return user, session_id

def get_user_info[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        user, session_id = await get_user(request)
        request.state.session_id = session_id
        request.state.user = user
        return await handle_request(request, *args, **kwargs)
    return wrapper

def require_logged_in(session_only=False):
    def require_logged_in_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            user, session_id = await get_user(request, session_only)
            if not user:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            request.state.session_id = session_id
            request.state.user = user
            return await handle_request(request, *args, **kwargs)
        return wrapper
    return require_logged_in_decorator

# if check_denied_only is True, as long as the permission is not denied we authorize the request
def require_permission(permission_name: str, check_denied_only = False, session_only = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            user, session_id = await get_user(request, session_only)
            if not user:
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

def require_team_permission(permission_name: str, check_denied_only = False, session_only = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            user, session_id = await get_user(request, session_only)
            if not user:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            team_id = request.path_params.get("team_id", None)
            if team_id is None:
                team_id = request.query_params.get("team_id", None)
            if team_id is None and request.method == "POST":
                body = await request.json()
                team_id = body.get("team_id", None)
            if team_id is None:
                raise Problem("No team ID specified", status=400)
            
            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, permission_name, check_denied_only, team_id=int(team_id)))

            if user_has_permission:
                request.state.session_id = session_id
                request.state.user = user
                return await handle_request(request, *args, **kwargs)
            else:
                raise Problem("Insufficient permission", f"User does not have required permission \'{permission_name}\'", status=401)
        return wrapper
    return has_permission_decorator

def require_series_permission(permission_name: str, check_denied_only = False, session_only = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            user, session_id = await get_user(request, session_only)
            if not user:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            # some things may be optionally part of a series, such as tournaments or tournament templates,
            # so we don't raise a problem if series_id is None for this function.
            series_id = request.path_params.get("series_id", None)
            if series_id is None:
                series_id = request.query_params.get("series_id", None)
            if series_id is None and request.method == "POST":
                body = await request.json()
                series_id = body.get("series_id", None)
            
            if series_id is not None:
                series_id = int(series_id)
            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, permission_name, check_denied_only, series_id=series_id))

            if user_has_permission:
                request.state.session_id = session_id
                request.state.user = user
                return await handle_request(request, *args, **kwargs)
            else:
                raise Problem("Insufficient permission", f"User does not have required permission \'{permission_name}\'", status=401)
        return wrapper
    return has_permission_decorator

def require_tournament_permission(permission_name: str, check_denied_only = False, session_only = False):
    def has_permission_decorator[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
            user, session_id = await get_user(request, session_only)
            if not user:
                resp = ProblemResponse(Problem("Not logged in", status=401))
                resp.delete_cookie("session")
                return resp
            
            tournament_id = request.path_params.get("tournament_id", None)
            if tournament_id is None:
                tournament_id = request.query_params.get("tournament_id", None)
            if tournament_id is None and request.method == "POST":
                body = await request.json()
                tournament_id = body.get("tournament_id", None)

            if tournament_id is None:
                raise Problem("No tournament ID specified", status=400)

            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, permission_name, check_denied_only, tournament_id=int(tournament_id)))

            if user_has_permission:
                request.state.session_id = session_id
                request.state.user = user
                return await handle_request(request, *args, **kwargs)
            else:
                raise Problem("Insufficient permission", f"User does not have required permission \'{permission_name}\'", status=401)
        return wrapper
    return has_permission_decorator

def check_series_visibility[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        series_id = request.path_params.get("series_id", None)
        if series_id is None:
            series_id = request.query_params.get("series_id", None)
        if series_id is None and request.method == "POST":
            body = await request.json()
            series_id = body.get("series_id", None)
        if series_id is None:
            raise Problem("No series ID specified", status=400)

        is_public = await handle(CheckSeriesVisibilityCommand(int(series_id)))
        if is_public:
            return await handle_request(request, *args, **kwargs)
        
        user, _ = await get_user(request)
        if not user:
            resp = ProblemResponse(Problem("Not logged in", status=401))
            resp.delete_cookie("session")
            return resp
        
        user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, series_permissions.VIEW_HIDDEN_SERIES, series_id=int(series_id)))
        if user_has_permission:
            return await handle_request(request, *args, **kwargs)
        else:
            raise Problem("Insufficient permission", f"User does not have required permission \'{series_permissions.VIEW_HIDDEN_SERIES}\'", status=401)
    return wrapper

def check_tournament_visiblity[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        tournament_id = request.path_params.get("tournament_id", None)
        if tournament_id is None:
            tournament_id = request.query_params.get("tournament_id", None)
        if tournament_id is None and request.method == "POST":
            body = await request.json()
            tournament_id = body.get("tournament_id", None)

        if tournament_id is None:
            raise Problem("No tournament ID specified", status=400)
        
        is_viewable = await handle(CheckTournamentVisibilityCommand(int(tournament_id)))
        # if the tournament is viewable, everyone should be able to view it
        if is_viewable:
            return await handle_request(request, *args, **kwargs)

        user, _ = await get_user(request)
        if not user:
            resp = ProblemResponse(Problem("Not logged in", status=401))
            resp.delete_cookie("session")
            return resp
        
        user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, tournament_permissions.VIEW_HIDDEN_TOURNAMENT, tournament_id=int(tournament_id)))

        if user_has_permission:
            return await handle_request(request, *args, **kwargs)
        else:
            raise Problem("Insufficient permission", f"User does not have required permission \'{tournament_permissions.VIEW_HIDDEN_TOURNAMENT}\'", status=401)
    return wrapper

# used to see if a user can view hidden posts
def check_post_privileges[**P](handle_request: Callable[Concatenate[Request, P], Awaitable[Response]]):
    async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs):
        user, _ = await get_user(request)
        request.state.user = user
        if user is None:
            request.state.is_privileged = False
            return await handle_request(request, *args, **kwargs)

        tournament_id = request.path_params.get('tournament_id', None)
        if tournament_id:
            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, tournament_permissions.MANAGE_TOURNAMENT_POSTS, tournament_id=int(tournament_id)))
            request.state.is_privileged = user_has_permission
            return await handle_request(request, *args, **kwargs)
        
        series_id = request.path_params.get('series_id', None)
        if series_id:
            user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, series_permissions.MANAGE_SERIES_POSTS, series_id=int(series_id)))
            request.state.is_privileged = user_has_permission
            return await handle_request(request, *args, **kwargs)
        
        user_has_permission = await handle(CheckUserHasPermissionCommand(user.id, permissions.MANAGE_POSTS))
        request.state.is_privileged = user_has_permission
        return await handle_request(request, *args, **kwargs)
    return wrapper