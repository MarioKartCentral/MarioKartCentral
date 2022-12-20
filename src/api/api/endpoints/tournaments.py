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
    try:
        tournament_name = request.query_params['name']
        date = int(request.query_params['date'])
        game = request.query_params['game']
        tournament_status = int(request.query_params['status'])
        description = request.query_params['description']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    async with connect_db() as db:
        cursor = await db.execute(
            "INSERT INTO tournaments(name, date, game, status) VALUES (?, ?, ?, ?)",
            (tournament_name, date, game, tournament_status))
        tournament_id = cursor.lastrowid
        await db.commit()

    s3_json = {"id": tournament_id, "description": description}
    s3_message = bytes(json.dumps(s3_json).encode('utf-8'))
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        result = await s3_client.put_object(Bucket='tournaments', Key=f'{tournament_id}.json', Body=s3_message)
    print(result)
    return JSONResponse({"id": tournament_id,
                    "name": tournament_name,
                    "date": date,
                    "game": game,
                    "status": tournament_status,
                    "description": description})

@require_permission(permissions.READ_S3)
async def tournament_info(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    async with connect_db() as db:
        async with db.execute("SELECT name, date, game, status FROM tournaments WHERE id = ?", (tournament_id, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'Invalid tournament ID'}, status_code=401)
            tournament_name = row[0]
            date = row[1]
            game = row[2]
            status = row[3]
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        response = await s3_client.get_object(Bucket='tournaments', Key=f'{tournament_id}.json')
        async with response['Body'] as stream:
            body = await stream.read()
            json_body = json.loads(body)
            description = json_body['description']
    return JSONResponse({
        "id": tournament_id,
        "name": tournament_name,
        "date": date,
        "game": game,
        "status": status,
        "description": description
    })
        
routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info)
]