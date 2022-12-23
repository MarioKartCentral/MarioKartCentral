import aiobotocore.session
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission
from api.s3 import create_s3_client
from api.db import connect_db
import json

@require_permission(permissions.WRITE_S3)
async def create_tournament(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        # there should be way more parameters than this in the final version;
        # however these are the minimum to make sure the basic functionality works
        tournament_name = body['name']
        date = int(body['date'])
        game = body['game']
        tournament_status = int(body['status'])
        description = body['description']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    # store minimal data about each tournament in the SQLite DB
    async with connect_db() as db:
        cursor = await db.execute(
            "INSERT INTO tournaments(name, date, game, status) VALUES (?, ?, ?, ?)",
            (tournament_name, date, game, tournament_status))
        tournament_id = cursor.lastrowid
        await db.commit()

    # store more detailed information about the tournament in object storage
    s3_json = {"id": tournament_id,
                "name": tournament_name,
                "date": date,
                "game": game,
                "status": tournament_status,
                "description": description}
    s3_message = bytes(json.dumps(s3_json).encode('utf-8'))
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        result = await s3_client.put_object(Bucket='tournaments', Key=f'{tournament_id}.json', Body=s3_message)
    return JSONResponse(s3_json)

@require_permission(permissions.READ_S3)
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

async def tournament_list_minimal(request: Request) -> JSONResponse:
    async with connect_db() as db:
        async with db.execute("SELECT id, name, date, game, status FROM tournaments") as cursor:
            rows = await cursor.fetchall()
    tournaments = []
    for row in rows:
        tournament = {}
        tournament['id'] = row[0]
        tournament['name'] = row[1]
        tournament['date'] = row[2]
        tournament['game'] = row[3]
        tournament['status'] = row[4]
        tournaments.append(tournament)
    return JSONResponse({"tournaments": tournaments})

async def tournament_list_basic(request: Request) -> JSONResponse:
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        response = await s3_client.list_objects_v2(Bucket='tournaments')
        object_list = response['Contents']
        tournaments = []
        for object in object_list:
            response = await s3_client.get_object(Bucket='tournaments', Key=object['Key'])
            async with response['Body'] as stream:
                body = await stream.read()
                tournament = json.loads(body)
                tournaments.append(tournament)
    return JSONResponse({'tournaments': tournaments})
        
routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info),
    Route('/api/tournaments/list', tournament_list_minimal),
    Route('/api/tournaments/list/basic', tournament_list_basic)
]