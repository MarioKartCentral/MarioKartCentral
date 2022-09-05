from datetime import datetime, timedelta, timezone
import os
import secrets
import aiosqlite
import boto3
from argon2 import PasswordHasher
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse
from starlette.routing import Route

hasher = PasswordHasher()

s3 = boto3.resource(
    service_name="s3",
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    endpoint_url=os.environ["S3_ENDPOINT"])

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
        await db.commit()

async def sign_up(request: Request) -> Response:
    body = await request.json()
    email = body["email"] # TODO: Email Verification
    password_hash = hasher.hash(body["password"])
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("INSERT INTO users(email, password_hash) VALUES (?, ?)", (email, password_hash)) as cursor:
            user_id = cursor.lastrowid
        await db.commit()
    
    return JSONResponse({'id': user_id, 'email': email}, status_code=201)

async def login(request: Request) -> Response:
    body = await request.json()
    email = body["email"]
    password = body["password"]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, password_hash FROM users WHERE email = ?", (email, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return Response("Invalid login details", status_code=401)
            user_id = row[0]
            password_hash = row[1]

    is_valid_password = hasher.verify(password_hash, password)
    if not is_valid_password:
        return Response("Invalid login details", status_code=401)
    
    session_id = secrets.token_hex(16)
    max_age = timedelta(days=365)
    expiration_date = datetime.now(timezone.utc) + max_age

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)", (session_id, user_id, expiration_date.timestamp()))
        await db.commit()

    resp = RedirectResponse('/', status_code=303)
    resp.set_cookie('session', session_id, max_age=max_age.total_seconds())
    return resp

async def logout(request: Request) -> Response:
    session_id = request.cookies["session"]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id, ))
        await db.commit()
    resp = RedirectResponse('/', status_code=303)
    resp.delete_cookie('session')
    return resp

async def current_user(request: Request) -> Response:
    session_id = request.cookies["session"]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT u.id, u.email, u.password_hash FROM users u JOIN sessions s on s.user_id = u.id WHERE session_id = ?", (session_id, )) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return Response("Not logged in", status_code=401)
            return JSONResponse({ 'id': row[0], 'email': row[1], 'password_hash': row[2] })

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

async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def s3_read(request: Request):
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    obj = s3.Object(bucket_name, file_name)

    body = obj.get()['Body'].read()

    return JSONResponse({
        f'{bucket_name} - {file_name}': 
        f'{body}'
    })

async def s3_write(request: Request):
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
        message = request.query_params['message']
    except RuntimeError:
        return JSONResponse({'error':'No correct body send'})

    message = message.encode('utf-8')

    result = s3.Object(bucket_name, file_name).put(Body=message)

    return JSONResponse(result)

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
]

app = Starlette(debug=True, routes=routes, on_startup=[init_db])
