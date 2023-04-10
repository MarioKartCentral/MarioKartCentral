from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import (CreateTeamCommand)
from common.data.models import (CreateTeamRequestData)

@bind_request_body(CreateTeamRequestData)
async def create_team(request: Request, body: CreateTeamRequestData) -> Response:
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
        body.logo, False, False, False)
    await handle(command)
    return JSONResponse({})

routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST'])
]