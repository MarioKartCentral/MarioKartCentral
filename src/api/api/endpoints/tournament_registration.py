import aiobotocore.session
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission
from api.s3 import create_s3_client
from api.db import connect_db
import json
from datetime import datetime

# helper function to register a player for a tournament, this is used in three endpoints so it is separated as its own function
async def register_player(player_id, tournament_id, squad_id, is_squad_captain, is_checked_in, mii_name, can_host, is_invite):
    timestamp = int(datetime.utcnow().timestamp())
    async with connect_db() as db:
        await db.execute("pragma foreign_keys = ON;")
        # check if player has already registered for the tournament
        async with db.execute("SELECT id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (player_id, tournament_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                return JSONResponse({'error': 'Player already registered for tournament'}, status_code=400)
        # check if mii name is required and if player's squad is at maximum number of players
        if squad_id is not None:
            async with db.execute("SELECT max_squad_size, mii_name_required FROM tournaments WHERE id = ?", (tournament_id)) as cursor:
                row = await cursor.fetchone()
                max_squad_size = row[0]
                mii_name_required = row[1]
                if mii_name_required == 1 and mii_name is None:
                    return JSONResponse({'error': 'Tournament requires a Mii Name'}, status_code=400)
            async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id = ?", (tournament_id, squad_id)) as cursor:
                player_squad_size = cursor.rowcount
                if player_squad_size == max_squad_size:
                    return JSONResponse({'error': 'Squad at maximum number of players'}, status_code=400)
        async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite)) as cursor:
            tournament_player_id = cursor.lastrowid
        await db.commit()
    json_resp = {
        'id': tournament_player_id,
        'player_id': player_id,
        'tournament_id': tournament_id,
        'squad_id': squad_id,
        'is_squad_captain': is_squad_captain,
        'timestamp': timestamp,
        'is_checked_in': is_checked_in,
        'mii_name': mii_name,
        'can_host': can_host,
        'is_invite': is_invite
    }
    return JSONResponse(json_resp, status_code=201)

# helper function to create a squad and register the passed in player for a tournament.
# this is used in two endpoints so it is separated as its own function.
async def create_squad(squad_name, squad_tag, squad_color, player_id, tournament_id, is_checked_in, mii_name, can_host, admin=False):
    timestamp = int(datetime.utcnow().timestamp())
    async with connect_db() as db:
        await db.execute("pragma foreign_keys = ON;")
        # check if player has already registered for the tournament
        async with db.execute("SELECT id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (player_id, tournament_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                return JSONResponse({'error': 'Player already registered for tournament'}, status_code=400)
        # check if tournament registrations are open
        async with db.execute("SELECT is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            is_squad = row[0]
            registrations_open = row[1]
            squad_tag_required = row[2]
            squad_name_required = row[3]
            mii_name_required = row[4]
            if is_squad == 0:
                return JSONResponse({'error': 'This is not a squad tournament'}, status_code=400)
            if admin is False and registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
            if squad_tag_required == 1 and squad_tag is None:
                return JSONResponse({'error': 'Tournament requires a tag for squads'}, status_code=400)
            if squad_name_required == 1 and squad_name is None:
                return JSONResponse({'error': 'Tournament requires a name for squads'}, status_code=400)
            if mii_name_required == 1 and mii_name is None:
                return JSONResponse({'error': 'Tournament requires a Mii Name'}, status_code=400)
        async with db.execute("""INSERT INTO tournament_squads(name, tag, color, timestamp, tournament_id)
            VALUES (?, ?, ?, ?, ?)""", (squad_name, squad_tag, squad_color, timestamp, tournament_id)) as cursor:
            squad_id = cursor.lastrowid
        await db.commit()

        async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (player_id, tournament_id, squad_id, 1, timestamp, is_checked_in, mii_name, can_host, 0)) as cursor:
            tournament_player_id = cursor.lastrowid
        await db.commit()
    resp = {
        'squad_id': squad_id,
        'squad_name': squad_name,
        'squad_tag': squad_tag,
        'squad_color': squad_color,
        'timestamp': timestamp,
        'tournament_id': tournament_id,
        'players': [
            {
                'id': tournament_player_id,
                'player_id': player_id,
                'is_squad_captain': True,
                'is_checked_in': is_checked_in,
                'mii_name': mii_name,
                'can_host': can_host,
                'is_invite': False
            }
        ]
    }
    return JSONResponse(resp, status_code=201)

# endpoint used when a user creates their own squad
async def create_my_squad(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_name = None
        squad_tag = None
        mii_name = None
        can_host = False
        if "squad_name" in body:
            squad_name = body['squad_name']
        if "squad_tag" in body:
            squad_tag = body['squad_tag']
        squad_color = body['squad_color']
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host'] 
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    is_checked_in = 0
    async with connect_db() as db:
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            player_id = row[0]
    json_resp = await create_squad(squad_name, squad_tag, squad_color, player_id, tournament_id, is_checked_in, mii_name, can_host)

# endpoint used when a tournament staff creates a squad with another user in it
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        squad_name = None
        squad_tag = None
        mii_name = None
        can_host = False
        if "squad_name" in body:
            squad_name = body['squad_name']
        if "squad_tag" in body:
            squad_tag = body['squad_tag']
        squad_color = body['squad_color']
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = 0
    json_resp = await create_squad(squad_name, squad_tag, squad_color, player_id, tournament_id, is_checked_in, mii_name, can_host)
    return json_resp

# used when the captain of a squad invites a player to their squad.
# use force_register_player in tournament staff contexts
async def invite_player(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = int(body['squad_id'])
        player_id = int(body['player_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    async with connect_db() as db:
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            squad_captain_id = row[0]
        # check captain's permissions
        async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_registrations WHERE player_id = ?, tournament_id = ?, is_invite = ?", (squad_captain_id, tournament_id, 0)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'You are not registered for this tournament'}, status_code=400)
            captain_squad_id = row[0]
            if captain_squad_id != squad_id:
                return JSONResponse({'error': 'You are not registered for this squad'}, status_code=400)
            is_squad_captain = row[1]
            if is_squad_captain == 0:
                return JSONResponse({'error': 'You are not captain of your squad'}, status_code=400)
        # make sure player isn't already registered
        async with db.execute("SELECT squad_id FROM tournament_registrations WHERE player_id = ?, tournament_id = ?, is_invite = ?", (player_id, tournament_id, 0)) as cursor:
            row = await cursor.fetchone()
            if row is not None:
                return JSONResponse({'error': 'Player is already registered for this tournament'}, status_code=400)
    json_resp = await register_player(player_id, tournament_id, squad_id, 0, 0, None, False, True)
    return json_resp

# endpoint used when a user registers themself for a tournament
async def register_me(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = None
        is_squad_captain = None
        mii_name = None
        can_host = False
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host']
        is_invite = int(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = 0
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            player_id = row[0]
    json_resp = await register_player(player_id, tournament_id, squad_id, is_squad_captain, is_checked_in, mii_name, can_host, is_invite)
    return json_resp

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        is_squad_captain = None
        squad_id = None
        mii_name = None
        can_host = False
        if "squad_id" in body:
            squad_id = body['squad_id']
        if "is_squad_captain" in body:
            is_squad_captain = body['is_squad_captain']
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host']
        is_invite = int(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = 0
    json_resp = await register_player(player_id, tournament_id, squad_id, is_squad_captain, is_checked_in, mii_name, can_host, is_invite)
    return json_resp

routes = [
    Route('/api/tournaments/{id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceRegister', force_register_player, methods=['POST']),
    Route('/api/tournaments/{id:int}/createSquad', create_my_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceCreateSquad', force_create_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/invitePlayer', invite_player, methods=['POST'])
]