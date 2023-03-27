from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission, require_logged_in
from api.data import handle_command, connect_db
from common.data.commands import CreatePlayerCommand

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
        switch_fc = body.get("switch_fc", None)
        mkw_fc = body.get("mkw_fc", None)
        mkt_fc = body.get("mkt_fc", None)
        nnid = body.get("nnid", None)
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id

    player_id = handle_command(
        CreatePlayerCommand(name, user_id, country_code, is_hidden, is_shadow, is_banned, discord_id, switch_fc, mkw_fc, mkt_fc, nnid))
    
    if player_id is None:
        return JSONResponse({'error': 'Error occurred when creating player'})
    
    return JSONResponse({ player_id: player_id }, status_code=201)

@require_permission(permissions.EDIT_PLAYER)
async def edit_player(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        player_id = int(body['player_id'])
        set_clauses = []
        variable_parameters = []
        if 'name' in body:
            set_clauses.append("name = ?")
            variable_parameters.append(body['name'])
        if 'country_code' in body:
            set_clauses.append("country_code = ?")
            variable_parameters.append(body['country_code'])
        if 'is_hidden' in body:
            set_clauses.append("is_hidden = ?")
            variable_parameters.append(int(body['is_hidden']))
        if 'is_shadow' in body:
            set_clauses.append("is_shadow = ?")
            variable_parameters.append(int(body['is_shadow']))
        if 'is_banned' in body:
            set_clauses.append("is_banned = ?")
            variable_parameters.append(int(body['is_banned']))
        if 'discord_id' in body:
            set_clauses.append("discord_id")
            variable_parameters.append(int(body['discord_id']))
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    # if we end up changing nothing about the player, give 400 error
    if len(set_clauses) == 0:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    set_clause = ", ".join(set_clauses)
    variable_parameters.append(player_id)
    async with connect_db() as db:
        async with db.execute(f"UPDATE players SET {set_clause} WHERE id = ?", variable_parameters) as cursor:
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                return JSONResponse({'error':'No player found'}, status_code=404)
        async with db.execute("SELECT * FROM players WHERE id = ?", (player_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
        await db.commit()

    resp = {
        'id': player_id,
        'name': row[1],
        'country_code': row[2],
        'is_hidden': row[3],
        'is_shadow': row[4],
        'is_banned': row[5],
        'discord_id': row[6]
    }
    return JSONResponse(resp, status_code=201)

async def view_player(request: Request) -> JSONResponse:
    player_id = request.path_params['id']
    async with connect_db() as db:
        async with db.execute("SELECT * FROM players WHERE id = ?", (player_id,)) as cursor:
            player_row = await cursor.fetchone()
            if player_row is None:
                return JSONResponse({'error':'No player found'}, status_code=404)
        async with db.execute("SELECT * FROM friend_codes WHERE player_id = ?", (player_id,)) as cursor:
            fc_rows = await cursor.fetchall()
    resp_fcs = []
    for fc in fc_rows:
        curr_fc = {
            'fc': fc[1],
            'is_verified': fc[2],
            'game': fc[3]
        }
        resp_fcs.append(curr_fc)
    resp = {
        'id': player_id,
        'name': player_row[1],
        'country_code': player_row[2],
        'is_hidden': player_row[3],
        'is_shadow': player_row[4],
        'is_banned': player_row[5],
        'discord_id': player_row[6],
        'friend_codes': resp_fcs
    }
    return JSONResponse(resp)

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