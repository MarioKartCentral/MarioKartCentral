import io

import aiosqlite
from minio import Minio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

minio_client = Minio(
    "s3-emulator:9000", 
    access_key="mkcdev", 
    secret_key="mk4thewin",
    secure=False
)

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

async def minio_read(request: Request):
    try:
        data = await request.json()
        bucket_name = data['bucket']
        file_name = data['file']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    print(bucket_name)
    print(file_name)

    try:
        response = minio_client.get_object(bucket_name, file_name)
        # Read data from response.
        return JSONResponse({
            '{b} - {fn}'.format(b=bucket_name, fn=file_name): 
            '{res}'.format(res=response.data.decode())
        })
    finally:
        response.close()
        response.release_conn()

async def minio_write(request):
    try:
        data = await request.json()
        bucket_name = data['bucket']
        file_name = data['file']
        message = data['message']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    if not minio_client.bucket_exists(bucket_name):
        print('creating {bucket}...'.format(bucket=bucket_name))
        minio_client.make_bucket(bucket_name)

    message = message.encode('utf-8')

    result = minio_client.put_object(
        bucket_name, 
        file_name, 
        io.BytesIO(message), 
        length=len(message)
    )    

    print(result.object_name)

    return JSONResponse(result.object_name)

routes = [
    Route('/api', homepage),
    Route('/api/user/list', list_users),
    Route('/api/minio', minio_read),
    Route('/api/minio', minio_write, methods=["POST"]),
    Route('/api/user', add_user, methods=["POST"])
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])
