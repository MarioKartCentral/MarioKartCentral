import io
import os

import aiosqlite
import boto3
from minio import Minio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

clientArgs = {
    'aws_access_key_id': os.environ["MINIO_ROOT_USER"],
    'aws_secret_access_key': os.environ["MINIO_ROOT_PASSWORD"],
    'endpoint_url': 'http://s3-emulator:9000/'
}
client = boto3.resource("s3", **clientArgs)

DB_PATH = "/var/lib/mkc-api/data/mkc.db"

DEBUG = False
if DEBUG:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()  # blocks execution until client is attached

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY)")
        await db.commit()

async def add_user(request: Request) -> Response:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO users VALUES (?)", [request.query_params["name"]])
        await db.commit()
    return Response(status_code=200)

async def list_users(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name FROM users") as cursor:
            names = [row[0] for row in await cursor.fetchall()]
    return JSONResponse({'users': names})

async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def s3_read(request: Request):
    try:
        data = await request.json()
        bucket_name = data['bucket']
        file_name = data['file']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    obj = client.Object(bucket_name, file_name)

    body = obj.get()['Body'].read()

    return JSONResponse({
        f'{bucket_name} - {file_name}': 
        f'{body}'
    })

async def s3_write(request):
    try:
        data = await request.json()
        bucket_name = data['bucket']
        file_name = data['file']
        message = data['message']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    message = message.encode('utf-8')

    result = client.Object(bucket_name, file_name).put(Body=message)

    return JSONResponse(result)

routes = [
    Route('/api', homepage),
    Route('/api/user/list', list_users),
    Route('/api/minio', s3_read),
    Route('/api/minio', s3_write, methods=["POST"]),
    Route('/api/user', add_user, methods=["POST"])
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])
