from starlette.requests import Request
from starlette.routing import Route
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from api.auth import require_tournament_permission, check_tournament_visiblity
from common.auth import tournament_permissions
from common.data.commands import *
from common.data.models import *

@bind_request_body(list[TournamentPlacement])
@require_tournament_permission(tournament_permissions.MANAGE_PLACEMENTS)
async def set_placements(request: Request, body: list[TournamentPlacement]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, False, False, False, None)
        registrations = await handle(reg_command)
        placements_command = SetSquadPlacementsCommand(tournament_id, body, registrations)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, False, False, None)
        registrations = await handle(reg_command)
        placements_command = SetSoloPlacementsCommand(tournament_id, body, registrations)

    await handle(placements_command)

    return JSONResponse({})

@bind_request_body(list[TournamentPlacementFromPlayerIDs])
@require_tournament_permission(tournament_permissions.MANAGE_PLACEMENTS)
async def set_placements_from_player_ids(request: Request, body: list[TournamentPlacementFromPlayerIDs]) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = SetSquadPlacementsFromPlayerIDsCommand(tournament_id, body)
    await handle(command)
    return JSONResponse({})

@check_tournament_visiblity
async def get_placements(request: Request) -> JSONResponse:
    tournament_id = int(request.path_params['tournament_id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, False, False, False, None)
        squads = await handle(reg_command)
        placements_command = GetSquadPlacementsCommand(tournament_id, squads)
        placements = await handle(placements_command)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, False, False, None)
        players = await handle(reg_command)
        placements_command = GetSoloPlacementsCommand(tournament_id, players)
        placements = await handle(placements_command)
    return JSONResponse(placements)

async def get_latest_tournament_with_placements(request: Request) -> JSONResponse:
    tournament_id = await handle(GetLatestTournamentIdWithPlacements())
    command = GetTournamentDataCommand(tournament_id)
    tournament = await handle(command)
    return JSONResponse(tournament)

async def get_player_placements(request: Request) -> JSONResponse:
    player_id = int(request.path_params['player_id'])
    placements_command = GetPlayerTournamentPlacementsCommand(player_id)
    placements = await handle(placements_command)
    return JSONResponse(placements)

async def get_team_placements(request: Request) -> JSONResponse:
    team_id = int(request.path_params['team_id'])
    command = GetTeamTournamentPlacementsCommand(team_id)
    placements = await handle(command)
    return JSONResponse(placements)


async def get_series_placements(request: Request) -> JSONResponse:
    series_id = int(request.path_params['id'])
    filter = TournamentFilter()
    filter.series_id = series_id
    list_command = GetTournamentListCommand(filter)
    tournaments = await handle(list_command)
    if len(tournaments) > 0:
        tournament_id = tournaments[0].id   
        command = CheckIfSquadTournament(tournament_id)
        is_squad = await handle(command)
        if is_squad:
            reg_command = GetSquadTournamentListWithPlacements(series_id)
            tournamentsWithPlacements = await handle(reg_command)
        else:
            reg_command = GetSoloTournamentListWithPlacements(series_id)
            tournamentsWithPlacements = await handle(reg_command)
        return JSONResponse(tournamentsWithPlacements)
    return JSONResponse({})


routes = [
    Route('/api/tournaments/{tournament_id:int}/placements/set', set_placements, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/placements/setFromPlayerIDs', set_placements_from_player_ids, methods=["POST"]),
    Route('/api/tournaments/{tournament_id:int}/placements', get_placements),
    Route('/api/tournaments/latestWithPlacements', get_latest_tournament_with_placements),
    Route('/api/tournaments/players/placements/{player_id:int}', get_player_placements),
    Route('/api/tournaments/teams/placements/{team_id:int}', get_team_placements)
]
