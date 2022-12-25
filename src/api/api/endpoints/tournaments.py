import aiobotocore.session
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission
from api.s3 import create_s3_client
from api.db import connect_db
import json

@require_permission(permissions.CREATE_TOURNAMENT)
async def create_tournament(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        # there should be way more parameters than this in the final version;
        # however these are the minimum to make sure the basic functionality works
        tournament_name = body['name']
        game = body['game']
        mode = body['mode']
        series_id = int(body['series_id'])
        is_squad = int(body['is_squad'])
        registrations_open = int(body['registrations_open'])
        date_start = int(body['date_start'])
        date_end = int(body['date_end'])
        description = body['description']
        logo = body['logo']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    # store minimal data about each tournament in the SQLite DB
    async with connect_db() as db:
        cursor = await db.execute(
            "INSERT INTO tournaments(name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (tournament_name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, logo))
        tournament_id = cursor.lastrowid
        await db.commit()

    # store more detailed information about the tournament in object storage
    s3_json = {"id": tournament_id,
                "name": tournament_name,
                "game": game,
                "mode": mode,
                "series_id": series_id,
                "is_squad": is_squad,
                "registrations_open": registrations_open,
                "date_start": date_start,
                "date_end": date_end,
                "description": description,
                "logo": logo
                }
    s3_message = bytes(json.dumps(s3_json).encode('utf-8'))
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        result = await s3_client.put_object(Bucket='tournaments', Key=f'{tournament_id}.json', Body=s3_message)
    return JSONResponse(s3_json)

async def tournament_info(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        try:
            response = await s3_client.get_object(Bucket='tournaments', Key=f'{tournament_id}.json')
        except s3_client.exceptions.NoSuchKey as e:
            return JSONResponse({'error':'No tournament found'}, status_code=404)
        async with response['Body'] as stream:
            body = await stream.read()
            json_body = json.loads(body)
    return JSONResponse(json_body)

async def tournament_list_minimal():
    async with connect_db() as db:
        async with db.execute("SELECT id, name, date_start, date_end, game FROM tournaments") as cursor:
            rows = await cursor.fetchall()
    tournaments = []
    for row in rows:
        tournament = {
            'id': row[0],
            'name': row[1],
            'date_start': row[2],
            'date_end': row[3],
            'game': row[4],
        }
        tournaments.append(tournament)
    return JSONResponse({"tournaments": tournaments})

async def tournament_list_basic():
    async with connect_db() as db:
        async with db.execute("SELECT id, name, game, mode, series_id, is_squad, registrations_open, description, date_start, date_end, logo FROM tournaments") as cursor:
            rows = await cursor.fetchall()
    tournaments = []
    for row in rows:
        tournament = {
            'id': row[0],
            'name': row[1],
            'game': row[2],
            'mode': row[3],
            'series_id': row[4],
            'is_squad': row[5],
            'registrations_open': row[6],
            'description': row[7],
            'date_start': row[8],
            'date_end': row[9],
            'logo': row[10]
        }
        tournaments.append(tournament)
    return JSONResponse({'tournaments': tournaments})

async def tournament_list(request:Request) -> JSONResponse:
    if 'detail' in request.query_params:
        if request.query_params['detail'] == 'basic':
            return await tournament_list_basic()
    return await tournament_list_minimal()

routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info),
    Route('/api/tournaments/list', tournament_list)
]