from starlette.requests import Request
from starlette.routing import Route
from api.utils.responses import JSONResponse, bind_request_body
from api.auth import require_tournament_permission, check_tournament_visiblity
from api.data import State
from common.auth import tournament_permissions
from common.data.commands import *
from common.data.models import *


@bind_request_body(list[TournamentPlacement])
@require_tournament_permission(tournament_permissions.MANAGE_PLACEMENTS)
async def set_placements(request: Request[State], body: list[TournamentPlacement]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    reg_command = GetTournamentRegistrationsCommand(
        tournament_id, False, False, False, None)
    registrations = await request.state.command_handler.handle(reg_command)
    placements_command = SetTournamentPlacementsCommand(
        tournament_id, body, registrations)
    await request.state.command_handler.handle(placements_command)

    return JSONResponse({})


@bind_request_body(list[TournamentPlacementFromPlayerIDs])
@require_tournament_permission(tournament_permissions.MANAGE_PLACEMENTS)
async def set_placements_from_player_ids(request: Request[State], body: list[TournamentPlacementFromPlayerIDs]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = SetTournamentPlacementsFromPlayerIDsCommand(tournament_id, body)
    await request.state.command_handler.handle(command)
    return JSONResponse({})


@check_tournament_visiblity
async def get_placements(request: Request[State]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    reg_command = GetTournamentRegistrationsCommand(
        tournament_id, False, False, False, None)
    squads = await request.state.command_handler.handle(reg_command)
    placements_command = GetTournamentPlacementsCommand(tournament_id, squads)
    placements = await request.state.command_handler.handle(placements_command)

    return JSONResponse(placements)


async def get_latest_tournament_with_placements(request: Request[State]) -> JSONResponse:
    tournament_id = await request.state.command_handler.handle(GetLatestTournamentIdWithPlacements())
    command = GetTournamentDataCommand(tournament_id)
    tournament = await request.state.command_handler.handle(command)
    return JSONResponse(tournament, headers={"Cache-Control": "public, max-age=600, s-maxage=600"})


async def get_player_placements(request: Request[State]) -> JSONResponse:
    player_id = int(request.path_params['player_id'])
    placements_command = GetPlayerTournamentPlacementsCommand(player_id)
    placements = await request.state.command_handler.handle(placements_command)
    return JSONResponse(placements)


async def get_team_placements(request: Request[State]) -> JSONResponse:
    team_id = int(request.path_params['team_id'])
    command = GetTeamTournamentPlacementsCommand(team_id)
    placements = await request.state.command_handler.handle(command)
    return JSONResponse(placements)


routes = [
    Route('/api/tournaments/{tournament_id:int}/placements/set',
          set_placements, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/placements/setFromPlayerIDs',
          set_placements_from_player_ids, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/placements', get_placements),
    Route('/api/tournaments/latestWithPlacements',
          get_latest_tournament_with_placements),
    Route(
        '/api/tournaments/players/placements/{player_id:int}', get_player_placements),
    Route(
        '/api/tournaments/teams/placements/{team_id:int}', get_team_placements)
]
