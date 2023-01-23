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
# returns 2 values: json response, status code (create_squad uses this but makes its own json response, so the two are separate)
async def register_player(player_id, tournament_id, squad_id, is_checked_in, mii_name, can_host, is_invite):
    timestamp = int(datetime.utcnow().timestamp())
    async with connect_db() as db:
        await db.execute("pragma foreign_keys = ON;")
        # check if player has already registered for the tournament
        async with db.execute("SELECT id from tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0", (player_id, tournament_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {'error': 'Player already registered for tournament'}, 400
        # check if player's squad is at maximum number of players
        if squad_id is not None:
            async with db.execute("SELECT max_squad_size FROM tournaments WHERE id = ?", (tournament_id)) as cursor:
                row = await cursor.fetchone()
                max_squad_size = row[0]
            async with db.execute("SELECT id FROM tournament_players WHERE tournament_id = ? AND squad_id = ?", (tournament_id, squad_id)) as cursor:
                player_squad_size = cursor.rowcount
                if player_squad_size == max_squad_size:
                    return {'error': 'Squad at maximum number of players'}, 400
        async with db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, timestamp, is_checked_in, mii_name, can_host, is_invite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (player_id, tournament_id, squad_id, timestamp, is_checked_in, mii_name, can_host, is_invite)) as cursor:
            tournament_player_id = cursor.lastrowid
        await db.commit()
    json_resp = {
        'id': tournament_player_id,
        'player_id': player_id,
        'tournament_id': tournament_id,
        'squad_id': squad_id,
        'timestamp': timestamp,
        'is_checked_in': is_checked_in,
        'mii_name': mii_name,
        'can_host': can_host,
        'is_invite': is_invite
    }
    return json_resp, 201

# endpoint used when a user creates their own squad
async def create_squad(request: Request) -> JSONResponse:
    body = await request.json()
    return JSONResponse({})

# endpoint used when a tournament staff creates a squad with another user in it
async def force_create_squad(request: Request) -> JSONResponse:
    body = await request.json()
    return JSONResponse({})

# endpoint used when a user registers themself for a tournament
async def register_me(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = body['squad_id']
        if "mii_name" in body:
            mii_name = body['mii_name']
        else:
            mii_name = None
        can_host = body['can_host']
        is_invite = int(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = 0
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id)) as cursor:
            row = await cursor.fetchone()
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id)) as cursor:
            row = await cursor.fetchone()
            player_id = row[0]
    json_resp, status_code = await register_player(player_id, tournament_id, squad_id, is_checked_in, mii_name, can_host, is_invite)
    return JSONResponse(json_resp, status_code=status_code)

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        squad_id = body['squad_id']
        if "mii_name" in body:
            mii_name = body['mii_name']
        else:
            mii_name = None
        can_host = body['can_host']
        is_invite = int(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = 0
    json_resp, status_code = await register_player(player_id, tournament_id, squad_id, is_checked_in, mii_name, can_host, is_invite)
    return JSONResponse(json_resp, status_code=status_code)

routes = [
    Route('/api/tournaments/{id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceRegister', force_register_player, methods=['POST'])
]