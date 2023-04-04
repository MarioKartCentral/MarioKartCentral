from dataclasses import dataclass
from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import connect_db, handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
from common.data.commands import CreateSquadCommand, GetPlayerIdForUserCommand, RegisterPlayerCommand

@dataclass
class CreateSquadRequestData:
    squad_color: str
    squad_name: str | None = None
    squad_tag: str | None = None
    mii_name: str | None = None
    can_host: bool = False

# endpoint used when a user creates their own squad
@bind_request_body(CreateSquadRequestData)
async def create_my_squad(request: Request, body: CreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    user_id = request.state.user_id
    player_id = await handle(GetPlayerIdForUserCommand(user_id))
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, player_id, tournament_id, False, body.mii_name, body.can_host)
    await handle(command)
    return JSONResponse({})

@dataclass
class ForceCreateSquadRequestData:
    player_id: int
    squad_color: str
    squad_name: str | None = None
    squad_tag: str | None = None
    mii_name: str | None = None
    can_host: bool = False

# endpoint used when a tournament staff creates a squad with another user in it
@bind_request_body(ForceCreateSquadRequestData)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_create_squad(request: Request, body: ForceCreateSquadRequestData) -> JSONResponse:
    tournament_id = request.path_params['id']
    command = CreateSquadCommand(body.squad_name, body.squad_tag, body.squad_color, body.player_id, tournament_id, False, body.mii_name, body.can_host)
    await handle(command)
    return JSONResponse({})

async def edit_squad(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = int(body['squad_id'])
        squad_name = None
        squad_tag = None
        if "squad_name" in body:
            squad_name = body['squad_name']
        if "squad_tag" in body:
            squad_tag = body['squad_tag']
        squad_color = body['squad_color']
        is_registered = int(body['is_registered'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    async with connect_db() as db:
        async with db.execute("UPDATE tournament_squads SET name = ?, tag = ?, color = ?, is_registered = ? WHERE id = ? AND tournament_id = ?", (squad_name, squad_tag, squad_color, is_registered, squad_id, tournament_id)) as cursor:
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                return JSONResponse({'error':'No squad found'}, status_code=404)
        await db.commit()
    resp = {
        'squad_id': squad_id,
        'squad_name': squad_name,
        'squad_tag': squad_tag,
        'squad_color': squad_color,
        'tournament_id': tournament_id,
        'is_registered': is_registered
    }
    return JSONResponse(resp, status_code=201)

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
            assert row is not None
            squad_captain_id = row[0]
        # check captain's permissions
        async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = ?", (squad_captain_id, tournament_id, 0)) as cursor:
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
        async with db.execute("SELECT squad_id FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = ?", (player_id, tournament_id, 0)) as cursor:
            row = await cursor.fetchone()
            existing_squad_id = None
            if row:
                existing_squad_id = row[0]
        if existing_squad_id is not None:
            # make sure player's squad isn't withdrawn before giving error
            async with db.execute("SELECT is_registered FROM tournament_squads WHERE squad_id = ?", (existing_squad_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                is_registered = row[0]
                if is_registered == 1:
                    return JSONResponse({'error': 'Player is already registered for this tournament'}, status_code=400)
    command = RegisterPlayerCommand(player_id, tournament_id, squad_id, False, False, None, False, True)
    await handle(command)
    return JSONResponse({})

# endpoint used when a user registers themself for a tournament
async def register_me(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = None
        is_squad_captain = False
        mii_name = None
        can_host = False
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host']
        is_invite = bool(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = False
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
    command = RegisterPlayerCommand(player_id, tournament_id, squad_id, is_squad_captain, is_checked_in, mii_name, can_host, is_invite)
    await handle(command)
    return JSONResponse({})

# endpoint used when a tournament staff registers another player for a tournament (requires permissions)
@require_permission(permissions.MANAGE_TOURNAMENT_REGISTRATIONS)
async def force_register_player(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        is_squad_captain = False
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
        is_invite = bool(body['is_invite'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    is_checked_in = False
    command = RegisterPlayerCommand(player_id, tournament_id, squad_id, is_squad_captain, is_checked_in, mii_name, can_host, is_invite)
    await handle(command)
    return JSONResponse({})

async def edit_registration(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        registration_id = int(body['registration_id'])
        player_id = int(body['player_id'])
        mii_name = None
        can_host = False
        if "mii_name" in body:
            mii_name = body['mii_name']
        if "can_host" in body:
            can_host = body['can_host']
        is_invite = int(body['is_invite'])
        is_checked_in = int(body['is_checked_in'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    async with connect_db() as db:
        # check if registration exists and get some values from it
        async with db.execute("SELECT squad_id, is_squad_captain, timestamp FROM tournament_players WHERE id = ?", (registration_id)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'No registration found'}, status_code=404)
            squad_id = row[0]
            is_squad_captain = row[1]
            timestamp = row[2]
        await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ?, is_checked_in = ? WHERE id = ? AND tournament_id = ? AND player_id = ?", (
            mii_name, can_host, is_invite, is_checked_in, registration_id, tournament_id, player_id))
        await db.commit()
    json_resp = {
        'id': registration_id,
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

async def accept_invite(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        mii_name = None
        can_host = False
        if 'mii_name' in body:
            mii_name = body['mii_name']
        if 'can_host' in body:
            can_host = body['can_host']
        invite_id = int(body['invite_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
        # get invite from id
        async with db.execute("SELECT player_id, squad_id, is_squad_captain, timestamp, is_checked_in, is_invite FROM tournament_players WHERE id = ?", (invite_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Invite cannot be found'}, status_code=400)
            invite_player_id = row[0]
            squad_id = row[1]
            is_squad_captain = row[2]
            timestamp = row[3]
            is_checked_in = row[4]
            is_invite = row[5]
            if is_invite == 0:
                return JSONResponse({'error': 'Not an invite'}, status_code=400)
            if invite_player_id != player_id:
                return JSONResponse({'error': 'Invited player ID different than accepting player ID'}, status_code=400)
        await db.execute("UPDATE tournament_players SET mii_name = ?, can_host = ?, is_invite = ? WHERE id = ?", (mii_name, can_host, 0, invite_id))
        await db.commit()
        json_resp = {
            'id': invite_id,
            'player_id': player_id,
            'tournament_id': tournament_id,
            'squad_id': squad_id,
            'is_squad_captain': is_squad_captain,
            'timestamp': timestamp,
            'is_checked_in': is_checked_in,
            'mii_name': mii_name,
            'can_host': can_host,
            'is_invite': 0
        }
        return JSONResponse(json_resp, status_code=201)

async def decline_invite(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        invite_id = int(body['invite_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
        # get invite from id
        async with db.execute("SELECT player_id, is_invite FROM tournament_players WHERE id = ?", (invite_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Invite cannot be found'}, status_code=400)
            invite_player_id = row[0]
            if invite_player_id != player_id:
                return JSONResponse({'error': 'Invited player ID different than accepting player ID'}, status_code=400)
            is_invite = row[1]
            if is_invite == 0:
                return JSONResponse({'error': 'Not an invite'}, status_code=400)
            if invite_player_id != player_id:
                return JSONResponse({'error': 'Invited player ID different than declining player ID'}, status_code=400)
        await db.execute("DELETE FROM tournament_players WHERE id = ?", (invite_id,))
        await db.commit()
    return JSONResponse({'success': 'Successfully rejected invitation'}, status_code=201)

async def unregister_player(tournament_id, player_id, squad_id=None):
    is_invite = 0
    async with connect_db() as db:
        async with db.execute("DELETE FROM tournament_players WHERE tournament_id = ? AND player_id = ? AND squad_id = ? AND is_invite = ?", (tournament_id, player_id, squad_id, is_invite)) as cursor:
            edited_rows = cursor.rowcount
            if edited_rows == 0:
                return JSONResponse({'error': 'Player not found in tournament'}, status_code=400)
    return JSONResponse({'success': 'Successfully unregistered player'}, status_code=201)

# used when a squad captain wants to remove a member from their squad
async def remove_player_from_squad(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        squad_id = int(body['squad_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            squad_captain_id = row[0]
        # check captain's permissions
        async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = ?", (squad_captain_id, tournament_id, 0)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'You are not registered for this tournament'}, status_code=400)
            captain_squad_id = row[0]
            if captain_squad_id != squad_id:
                return JSONResponse({'error': 'You are not registered for this squad'}, status_code=400)
            is_squad_captain = row[1]
            if is_squad_captain == 0:
                return JSONResponse({'error': 'You are not captain of your squad'}, status_code=400)
    json_resp = await unregister_player(tournament_id, player_id, squad_id=squad_id)
    return json_resp

# used when a player unregisters themself from the tournament
async def unregister_me(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        squad_id = None
        if 'squad_id' in body:
            squad_id = int(body['squad_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    user_id = request.state.user_id
    async with connect_db() as db:
        # check if tournament registrations are open
        async with db.execute("SELECT registrations_open FROM tournaments WHERE ID = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            registrations_open = row[0]
            if registrations_open == 0:
                return JSONResponse({'error': 'Tournament registrations are closed'}, status_code=400)
        # get player id from user id in request
        async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
    json_resp = await unregister_player(tournament_id, player_id, squad_id=squad_id)
    return json_resp

# used when a staff member force removes a player from the tournament
async def staff_unregister(request: Request) -> JSONResponse:
    body = await request.json()
    tournament_id = request.path_params['id']
    try:
        player_id = int(body['player_id'])
        squad_id = None
        if 'squad_id' in body:
            squad_id = int(body['squad_id'])
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    json_resp = await unregister_player(tournament_id, player_id, squad_id=squad_id)
    return json_resp

async def view_squad(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    squad_id = request.path_params['squad_id']
    async with connect_db() as db:
        async with db.execute("SELECT name, tag, color, timestamp, is_registered FROM tournament_squads WHERE id = ? AND tournament_id = ?", (squad_id, tournament_id)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return JSONResponse({'error': 'Squad not found'}, status_code=400)
            squad_name = row[0]
            squad_tag = row[1]
            squad_color = row[2]
            timestamp = row[3]
            is_registered = row[4]
        async with db.execute("SELECT id, player_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite FROM tournament_players WHERE squad_id = ?",
            (squad_id,)) as cursor:
            rows = await cursor.fetchall()
            players = []
            for row in rows:
                curr_player = {
                    'id': row[0],
                    'player_id': row[1],
                    'is_squad_captain': row[2],
                    'timestamp': row[3],
                    'is_checked_in': row[4],
                    'mii_name': row[5],
                    'can_host': row[6],
                    'is_invite': row[7]
                }
                players.append(curr_player)
    json_resp = {
        'squad_id': squad_id,
        'squad_name': squad_name,
        'squad_tag': squad_tag,
        'squad_color': squad_color,
        'timestamp': timestamp,
        'tournament_id': tournament_id,
        'is_registered': is_registered,
        'players': players
    }
    return JSONResponse(json_resp)

async def squad_registrations(tournament_id, eligible_only):
    where_clause = ""
    if eligible_only:
        where_clause = "AND is_registered = 1"
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? {where_clause}", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            squads = {}
            for row in rows:
                squad_id = int(row[0])
                curr_squad = {
                    'id': squad_id,
                    'name': row[1],
                    'tag': row[2],
                    'color': row[3],
                    'timestamp': row[4],
                    'is_registered': row[5],
                    'players': []
                }
                squads[squad_id] = curr_squad
        async with db.execute(f"SELECT id, player_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite FROM tournament_players WHERE tournament_id = ?", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                squad_id = int(row[2])
                if squad_id not in squads:
                    continue
                curr_player = {
                    'id': row[0],
                    'player_id': row[1],
                    'is_squad_captain': row[3],
                    'timestamp': row[4],
                    'is_checked_in': row[5],
                    'mii_name': row[6],
                    'can_host': row[7],
                    'is_invite': row[8]
                }
                squads[squad_id]['players'].append(curr_player)
    return JSONResponse({'squads': [s for s in squads.values()]})
            

async def ffa_registrations(tournament_id):
    async with connect_db() as db:
        async with db.execute("SELECT id, player_id, timestamp, is_checked_in, mii_name, can_host FROM tournament_players WHERE tournament_id = ?", (tournament_id,)) as cursor:
            rows = await cursor.fetchall()
            players = []
            for row in rows:
                curr_player = {
                    'id': row[0],
                    'player_id': row[1],
                    'timestamp': row[2],
                    'is_checked_in': row[3],
                    'mii_name': row[4],
                    'can_host': row[5],
                }
                players.append(curr_player)
    return JSONResponse({'players': players})


async def list_registrations(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    eligible_only = False
    if "eligibleOnly" in request.query_params:
        eligible_only = True
    async with connect_db() as db:
        async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (tournament_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'Tournament not found'}, status_code=404)
            is_squad = row[0]
    if is_squad == 1:
        return await squad_registrations(tournament_id, eligible_only)
    return await ffa_registrations(tournament_id)

routes = [
    Route('/api/tournaments/{id:int}/register', register_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceRegister', force_register_player, methods=['POST']),
    Route('/api/tournaments/{id:int}/editRegistration', edit_registration, methods=['POST']),
    Route('/api/tournaments/{id:int}/createSquad', create_my_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceCreateSquad', force_create_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/editSquad', edit_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/invitePlayer', invite_player, methods=['POST']),
    Route('/api/tournaments/{id:int}/acceptInvite', accept_invite, methods=['POST']),
    Route('/api/tournaments/{id:int}/declineInvite', decline_invite, methods=['POST']),
    Route('/api/tournaments/{id:int}/kickPlayer', remove_player_from_squad, methods=['POST']),
    Route('/api/tournaments/{id:int}/unregister', unregister_me, methods=['POST']),
    Route('/api/tournaments/{id:int}/forceUnregister', staff_unregister, methods=['POST']),
    Route('/api/tournaments/{id:int}/squads/{squad_id:int}', view_squad),
    Route('/api/tournaments/{id:int}/registrations', list_registrations)
]