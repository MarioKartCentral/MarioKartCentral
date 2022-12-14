import aiosqlite
import aiobotocore.session
from argon2 import PasswordHasher
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import redis.asyncio as redis
from api.auth import current_user_has_permission
from api.constants import *
import api.services.authservice as authservice
import api.services.userservice as userservice
import api.services.roleservice as roleservice

DEBUG = False
RESET_DATABASE = False

hasher = PasswordHasher()
redis_conn = redis.from_url(REDIS_URL, decode_responses=True)

if DEBUG:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()  # blocks execution until client is attached


async def init_db():
    if RESET_DATABASE:
        open(DB_PATH, 'w').close()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("pragma journal_mode = WAL;")
        await db.execute("pragma synchronous = NORMAL;")
        await db.execute("pragma foreign_keys = ON;")
        await db.execute("""CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            email TEXT UNIQUE,
            password_hash TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id),
            expires_on INTEGER NOT NULL) WITHOUT ROWID""")
        await db.execute("""CREATE TABLE IF NOT EXISTS roles(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS permissions(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS user_roles(
            user_id INTEGER NOT NULL REFERENCES users(id),
            role_id INTEGER NOT NULL REFERENCES roles(id),
            PRIMARY KEY (user_id, role_id)) WITHOUT ROWID""")
        await db.execute("""CREATE TABLE IF NOT EXISTS role_permissions(
            role_id INTEGER NOT NULL REFERENCES roles(id),
            permission_id INTEGER NOT NULL REFERENCES permissions(id),
            PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID""")
        await db.commit()

        # create some default roles and permissions
        roles = [(0, 'Super Administrator'), (1, 'Administrator')]
        permissions = [(0, 'grant_administrator'),
                       (1, 's3_read'), (2, 's3_write')]

        # assign permissions to roles
        role_permissions = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2)]

        await db.executemany("INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING", roles)
        await db.executemany("INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING", permissions)
        await db.executemany("INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING", role_permissions)

        # create the root admin user and give it Super Administrator
        await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?) ON CONFLICT DO NOTHING", (ADMIN_EMAIL, hasher.hash(ADMIN_PASSWORD)))
        await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

        await db.commit()


async def homepage(request):
    return JSONResponse({'hello': 'world'})


def create_s3_client(session: aiobotocore.session.AioSession):
    return session.create_client(
        's3',
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        endpont_url=AWS_ENDPOINT_URL)


async def s3_read(request: Request) -> JSONResponse:
    if not await current_user_has_permission(request, 's3_read'):
        return JSONResponse({'error': 'Unauthorized to read from S3'}, status_code=401)

    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']

    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        response = await s3_client.get_object(Bucket=bucket_name, Key=file_name)
        async with response['Body'] as stream:
            body = await stream.read()

    return JSONResponse({
        f'{bucket_name} - {file_name}':
        f'{body}'
    })


async def s3_write(request: Request) -> JSONResponse:
    if not await current_user_has_permission(request, 's3_write'):
        return JSONResponse({'error': 'Unauthorized to write to S3'}, status_code=401)

    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
        message = request.query_params['message']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    message = message.encode('utf-8')

    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        result = await s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=message)

    return JSONResponse(result)


async def redis_write(request: Request) -> JSONResponse:
    text = request.path_params['text']
    await redis_conn.append("test", text)
    values = await redis_conn.get("test")
    return JSONResponse({'test': values})

routes = [
    Route('/api', homepage),
    Route('/api/s3', s3_read),
    Route('/api/s3', s3_write, methods=["POST"]),
    *authservice.get_routes(),
    *userservice.get_routes(),
    *roleservice.get_routes(),
    Route('/api/redis_write/{text:str}', redis_write),
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])
