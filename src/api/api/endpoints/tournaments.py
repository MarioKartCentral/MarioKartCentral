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
            return JSONResponse({'error':'Invalid tournament ID'}, status_code=401)
        async with response['Body'] as stream:
            body = await stream.read()
            json_body = json.loads(body)
    return JSONResponse(json_body)
        
routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info)
]