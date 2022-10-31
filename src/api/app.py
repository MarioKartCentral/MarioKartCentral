from datetime import datetime, timedelta, timezone
import os
import secrets
import aiosqlite
import aiobotocore.session
from argon2 import PasswordHasher
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse
from starlette.routing import Route
import redis.asyncio as redis

hasher = PasswordHasher()
redis_conn = redis.Redis(host='redis', port=6379, decode_responses=True)

AWS_ACCESS_KEY_ID=os.environ["S3_ACCESS_KEY"]
AWS_SECRET_ACCESS_KEY=os.environ["S3_SECRET_KEY"]
AWS_ENDPOINT_URL=os.environ["S3_ENDPOINT"]
ADMIN_EMAIL=os.environ["API_ADMIN_EMAIL"]
ADMIN_PASSWORD=os.environ["API_ADMIN_PASSWORD"]

DB_PATH = "/var/lib/mkc-api/data/mkc.db"
DEBUG = False
RESET_DATABASE = False

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
            name TEXT NOT NULL)""")
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
        roles = [ (0, 'Super Administrator'), (1, 'Administrator') ]
        permissions = [ (0, 'grant_administrator'), (1, 's3_read'), (2, 's3_write') ]
        role_permissions = [ (0, 0), (0, 1), (0, 2), (1, 1), (1, 2) ] # assign permissions to roles
        
        await db.executemany("INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING", roles)
        await db.executemany("INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING", permissions)
        await db.executemany("INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING", role_permissions)

        # create the root admin user and give it Super Administrator
        await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?) ON CONFLICT DO NOTHING", (ADMIN_EMAIL, hasher.hash(ADMIN_PASSWORD)))
        await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

        await db.commit()

async def current_user_has_permission(request: Request, permission_name: str):
    session_id = request.cookies.get("session", None)
    if session_id is None:
        return False

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT EXISTS(
                SELECT 1 FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                JOIN sessions s on s.user_id = u.id
                JOIN role_permissions rp on rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ?
            )""", (session_id, permission_name)) as cursor:
            row = await cursor.fetchone()
            return row is not None and bool(row[0])

async def sign_up(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"] # TODO: Email Verification
    password_hash = hasher.hash(body["password"])
    async with aiosqlite.connect(DB_PATH) as db:
        user_id = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (email, password_hash))
        await db.commit()
    
    return JSONResponse({'id': user_id, 'email': email}, status_code=201)

async def login(request: Request) -> JSONResponse:
    body = await request.json()
    email = body["email"]
    password = body["password"]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, password_hash FROM users WHERE email = ?", (email, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'Invalid login details'}, status_code=401)
            user_id = row[0]
            password_hash = row[1]

    try:
        is_valid_password = hasher.verify(password_hash, password)
        if not is_valid_password:
            return JSONResponse({'error':'Invalid login details'}, status_code=401)
    except:
        return JSONResponse({'error':'Invalid login details'}, status_code=401)

    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)", (session_id, user_id, expiration_date.timestamp()))
        await db.commit()

    resp = JSONResponse({}, status_code=200)
    resp.set_cookie('session', session_id, max_age=int(max_age.total_seconds()))
    return resp

async def logout(request: Request) -> JSONResponse:
    session_id = request.cookies.get("session", None)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id, ))
        await db.commit()
    resp = JSONResponse({}, status_code=200)
    resp.delete_cookie('session')
    return resp

async def current_user(request: Request) -> JSONResponse:
    session_id = request.cookies.get("session", None)
    if session_id is None:
        return JSONResponse({'error': 'Not logged in'}, status_code=401)

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT u.id, u.email, u.password_hash FROM users u JOIN sessions s on s.user_id = u.id WHERE session_id = ?", (session_id, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error':'Not logged in'}, status_code=401)
            user_id = row[0]
            user_email = row[1]
            user_pw_hash = row[2]

        roles_rows = await db.execute_fetchall("SELECT r.name FROM roles r JOIN user_roles ur on ur.role_id = r.id WHERE ur.user_id = ?", (user_id,))
        roles = [row[0] for row in roles_rows]
        return JSONResponse({ 'id': user_id, 'email': user_email, 'password_hash': user_pw_hash, 'roles': roles })

async def list_users(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, email, password_hash FROM users") as cursor:
            names = [{ 'id': row[0], 'email': row[1], 'password_hash': row[2] } for row in await cursor.fetchall()]
    return JSONResponse({'users': names})

async def list_players(request: Request) -> JSONResponse:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name FROM players") as cursor:
            names = [{ 'id': row[0], 'name': row[1] } for row in await cursor.fetchall()]
    return JSONResponse({'users': names})

async def grant_administrator(request: Request) -> JSONResponse:
    if not await current_user_has_permission(request, 'grant_administrator'):
        return JSONResponse({'error':'Unauthorized to grant administrator'}, status_code=401)
    
    body = await request.json()
    user_id = body["user_id"]

    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, 1)", (user_id,))
            await db.commit()
        except Exception as e:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return JSONResponse({'error':'User not found with given ID'}, status_code=404)
                else:
                    return JSONResponse({'error':'Unexpected error'}, status_code=500)

    return JSONResponse({}, status_code=200)

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
        return JSONResponse({'error':'Unauthorized to read from S3'}, status_code=401)

    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']

    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

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
        return JSONResponse({'error':'Unauthorized to write to S3'}, status_code=401)

    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
        message = request.query_params['message']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

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
    Route('/api/user/signup', sign_up, methods=["POST"]),
    Route('/api/user/login', login, methods=["POST"]),
    Route('/api/user/logout', logout, methods=["POST"]),
    Route('/api/player/list', list_players),
    Route('/api/user/list', list_users),
    Route('/api/user/me', current_user),
    Route('/api/user/grant_admin', grant_administrator),
    Route('/api/redis_write/{text:str}', redis_write),
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])
