import aiosqlite
from api import settings

def connect_db():
    return aiosqlite.connect(settings.DB_PATH)

async def init_db():
    from api.auth import roles, permissions, pw_hasher
    
    if settings.RESET_DATABASE:
        open(settings.DB_PATH, 'w').close()

    async with connect_db() as db:
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
        await db.execute("""CREATE TABLE IF NOT EXISTS tournaments(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date INTEGER NOT NULL,
            game TEXT NOT NULL,
            mode TEXT NOT NULL,
            series_id INTEGER,
            is_squad INTEGER NOT NULL,
            is_completed INTEGER NOT NULL,
            description TEXT NOT NULL,
            logo TEXT
            )""")
        await db.commit()

        await db.executemany(
            "INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
            roles.default_roles_by_id.items())

        await db.executemany(
            "INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
            permissions.permissions_by_id.items())

        await db.executemany(
            "INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            roles.default_role_permission_ids)

        # create the root admin user and give it Super Administrator
        await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?) ON CONFLICT DO NOTHING", (settings.ADMIN_EMAIL, pw_hasher.hash(str(settings.ADMIN_PASSWORD))))
        await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")

        await db.commit()