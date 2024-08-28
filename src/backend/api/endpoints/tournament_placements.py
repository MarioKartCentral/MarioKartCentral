from starlette.requests import Request
from starlette.routing import Route
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.data.commands import *
from common.data.models import *

@bind_request_body(list[TournamentPlacement])
async def set_placements(request: Request, body: list[TournamentPlacement]) -> JSONResponse:
    tournament_id = int(request.path_params['id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, True, True, False)
        registrations = await handle(reg_command)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, False)
        registrations = await handle(reg_command)

    placements_command = SetPlacementsCommand(tournament_id, is_squad, body, registrations)
    await handle(placements_command)

    return JSONResponse({})


async def get_placements(request: Request) -> JSONResponse:
    tournament_id = int(request.path_params['id'])
    command = CheckIfSquadTournament(tournament_id)
    is_squad = await handle(command)
    if is_squad:
        reg_command = GetSquadRegistrationsCommand(tournament_id, True, True, False)
        squads = await handle(reg_command)
        placements_command = GetSquadPlacementsCommand(tournament_id, squads)
        placements = await handle(placements_command)
    else:
        reg_command = GetFFARegistrationsCommand(tournament_id, False)
        players = await handle(reg_command)
        placements_command = GetSoloPlacementsCommand(tournament_id, players)
        placements = await handle(placements_command)
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
    Route('/api/tournaments/{id:int}/placements/set', set_placements, methods=["POST"]),
    Route('/api/tournaments/{id:int}/placements', get_placements),
    Route('/api/tournaments/series/{id:int}/placements', get_series_placements)
]