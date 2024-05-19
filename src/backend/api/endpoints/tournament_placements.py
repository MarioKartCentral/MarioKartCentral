from starlette.requests import Request
from starlette.routing import Route
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body
from common.data.commands import *
from common.data.models import *

@bind_request_body(list[TournamentPlacement])
async def set_placements(request: Request, body: list[TournamentPlacement]) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = SetPlacementsCommand(tournament_id, body)
    await handle(command)
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



routes = [
    Route('/api/tournaments/{id:int}/placements/set', set_placements, methods=["POST"]),
    Route('/api/tournaments/{id:int}/placements', get_placements)
]