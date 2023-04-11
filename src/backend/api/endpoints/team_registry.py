from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import (CreateTeamCommand, GetTeamInfoCommand)
from common.data.models import (CreateTeamRequestData)

@bind_request_body(CreateTeamRequestData)
async def create_team(request: Request, body: CreateTeamRequestData) -> JSONResponse:
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
        body.logo, False, False, body.game, body.mode, body.is_recruiting, True, False)
    await handle(command)
    return JSONResponse({})

async def view_team(request: Request) -> JSONResponse:
    team_id = request.path_params['id']
    command = GetTeamInfoCommand(team_id)
    team = await handle(command)
    return JSONResponse(team)


routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST']),
    Route('/api/registry/teams/{id:int}', view_team)
]