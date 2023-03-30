from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission, require_logged_in
from api.data import handle_command, connect_db
from api.utils.responses import OrjsonResponse, ProblemJsonResponse
from common.data.commands import CreatePlayerCommand, GetPlayerDetailedCommand, UpdatePlayerCommand
from common.data.models import Error

@require_logged_in
async def create_player(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        name = body['name']
        country_code = body['country_code']
        is_hidden = bool(body['is_hidden'])
        is_shadow = bool(body['is_shadow'])
        is_banned = bool(body['is_banned'])
        discord_id = body['discord_id']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id

    command = CreatePlayerCommand(name, user_id, country_code, is_hidden, is_shadow, is_banned, discord_id)
    player = await handle_command(command)
    
    if isinstance(player, Error):
        return ProblemJsonResponse(player, status_code=500)
    
    return OrjsonResponse(player, status_code=201)

@require_permission(permissions.EDIT_PLAYER)
async def edit_player(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        player_id = int(body['player_id'])
        name = body['name']
        country_code = body['country_code']
        is_hidden = bool(body['is_hidden'])
        is_shadow = bool(body['is_shadow'])
        is_banned = bool(body['is_banned'])
        discord_id = body['discord_id']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    
    command = UpdatePlayerCommand(player_id, name, country_code, is_hidden, is_shadow, is_banned, discord_id)
    succeeded = await handle_command(command)
    
    if not succeeded:
        return JSONResponse({'error': 'Player does not exist'}, status_code=404)
    
    return JSONResponse({}, status_code=200)

async def view_player(request: Request) -> JSONResponse:
    player_id = request.path_params['id']
    player_detailed = await handle_command(GetPlayerDetailedCommand(player_id))
    if player_detailed is None:
        return JSONResponse({'error': 'Player does not exist'}, status_code=404)

    return OrjsonResponse(player_detailed)

async def list_players(request: Request) -> JSONResponse:
    where_clauses = []
    variable_parameters = []
    # the below two arrays are for the case where we need to query the friend codes table
    # inside our main query, it's better to just query it once for the search results we need
    # rather than having to write multiple subqueries of the same table in the same query.
    subquery_where_clauses = []
    subquery_variable_parameters = []
    # we use LIKE for name and FC parameters to be able to search substrings
    if 'name' in request.query_params:
        where_clauses.append("name LIKE ?")
        variable_parameters.append(f"%{request.query_params['name']}%")
    if 'friend_code' in request.query_params:
        subquery_where_clauses.append("fc LIKE ?")
        subquery_variable_parameters.append(f"%{request.query_params['friend_code']}%")
    # the best way to check if a player plays a certain game is to just check the FC table
    # to see if they have an FC for that game.
    if 'game' in request.query_params:
        subquery_where_clauses.append("game = ?")
        subquery_variable_parameters.append(request.query_params['game'])
    if 'country' in request.query_params:
        where_clauses.append("country_code = ?")
        variable_parameters.append(request.query_params['country_code'])
    if 'is_hidden' in request.query_params:
        where_clauses.append("is_hidden = ?")
        variable_parameters.append(1)
    if 'is_shadow' in request.query_params:
        where_clauses.append("is_shadow = ?")
        variable_parameters.append(1)
    if 'is_banned' in request.query_params:
        where_clauses.append("is_banned = ?")
        variable_parameters.append(1)
    if 'discord_id' in request.query_params:
        where_clauses.append("discord_id = ?")
        variable_parameters.append(int(request.query_params['discord_id']))
    # finally constructing the fc table subquery
    if len(subquery_where_clauses) > 0:
        subquery_where_clause = f"WHERE {' AND '.join(subquery_where_clauses)}"
        # subquery returns a list of player ids where the clauses are true
        where_clauses.append(f"id IN (SELECT player_id FROM friend_codes {subquery_where_clause})")
        variable_parameters.extend(subquery_variable_parameters)
    where_clause = ""
    if len(where_clauses) > 0:
        where_clause = f"WHERE {' AND '.join(where_clauses)}"
    async with connect_db() as db:
        async with db.execute(f"SELECT * FROM players {where_clause}", variable_parameters) as cursor:
            rows = await cursor.fetchall()
        players = []
        for row in rows:
            player = {
                'id': row[0],
                'name': row[1],
                'country_code': row[2],
                'is_hidden': row[3],
                'is_shadow': row[4],
                'is_banned': row[5],
                'discord_id': row[6]
            }
            players.append(player)
        return JSONResponse({'players': players})

routes = [
    Route('/api/registry/players/create', create_player, methods=['POST']),
    Route('/api/registry/players/edit', edit_player, methods=['POST']),
    Route('/api/registry/players/{id:int}', view_player),
    Route('/api/registry/players', list_players)
]