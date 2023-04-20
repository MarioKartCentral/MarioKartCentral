from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from api.auth import require_permission, require_logged_in
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands import (CreateTeamCommand, EditRosterCommand, GetTeamInfoCommand, EditTeamCommand, CreateRosterCommand, InvitePlayerCommand)
from common.data.models import (CreateTeamRequestData, CreateRosterRequestData, EditRosterRequestData, InviteRosterPlayerRequestData)

@bind_request_body(CreateTeamRequestData)
async def create_team(request: Request, body: CreateTeamRequestData) -> JSONResponse:
    command = CreateTeamCommand(body.name, body.tag, body.description, body.language, body.color,
        body.logo, body.approval_status, body.is_historical, body.game, body.mode, body.is_recruiting, body.is_active, True)
    await handle(command)
    return JSONResponse({})

async def view_team(request: Request) -> JSONResponse:
    team_id = request.path_params['id']
    command = GetTeamInfoCommand(team_id)
    team = await handle(command)
    return JSONResponse(team)

@bind_request_body(CreateTeamRequestData)
async def edit_team(request: Request, body: CreateTeamRequestData) -> JSONResponse:
    team_id = request.path_params['id']
    command = EditTeamCommand(team_id, body.name, body.tag, body.description, body.language, body.color,
        body.logo, body.approval_status, body.is_historical, body.game, body.mode, body.is_recruiting, body.is_active, True)
    await handle(command)
    return JSONResponse({})

@bind_request_body(CreateRosterRequestData)
async def create_roster(request: Request, body: CreateRosterRequestData) -> JSONResponse:
    command = CreateRosterCommand(body.team_id, body.game, body.mode, body.name, body.tag, body.is_recruiting, body.is_active, body.approval_status)
    await handle(command)
    return JSONResponse({})

@bind_request_body(EditRosterRequestData)
async def edit_roster(request: Request, body: EditRosterRequestData) -> JSONResponse:
    command = EditRosterCommand(body.roster_id, body.team_id, body.name, body.tag, body.is_recruiting,
                                body.is_active, body.approval_status)
    await handle(command)
    return JSONResponse({})

@bind_request_body(InviteRosterPlayerRequestData)
async def invite_player(request: Request, body: InviteRosterPlayerRequestData) -> JSONResponse:
    command = InvitePlayerCommand(body.player_id, body.roster_id)
    await handle(command)
    return JSONResponse({})

routes: list[Route] = [
    Route('/api/registry/teams/create', create_team, methods=['POST']),
    Route('/api/registry/teams/{id:int}', view_team),
    Route('/api/registry/teams/{id:int}/edit', edit_team, methods=['POST']),
    Route('/api/registry/teams/createRoster', create_roster, methods=['POST']),
    Route('/api/registry/teams/editRoster', edit_roster, methods=['POST']),
    Route('/api/registry/teams/invitePlayer', invite_player, methods=['POST'])
]