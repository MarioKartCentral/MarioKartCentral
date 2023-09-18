from dataclasses import dataclass
from common.auth import permissions, roles, team_permissions, team_roles
from common.data.commands import Command
from common.data.db.tables import all_tables

class ResetDbCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        db_wrapper.reset_db()

class InitializeDbSchemaCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("pragma journal_mode = WAL;")
            await db.execute("pragma synchronous = NORMAL;")
            for table in all_tables:
                await db.execute(table.get_create_table_command())

@dataclass
class SeedDatabaseCommand(Command[None]):
    admin_email: str
    hashed_pw: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.executemany(
                "INSERT INTO roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_roles_by_id.items())
            
            await db.executemany(
                "INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                roles.default_role_permission_ids)
            
            await db.executemany(
                "INSERT INTO team_roles(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                team_roles.default_roles_by_id.items())
            
            await db.executemany(
                "INSERT INTO team_permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                team_permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO team_role_permissions(role_id, permission_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                team_roles.default_role_permission_ids)
            
            await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?)  ON CONFLICT DO NOTHING", (self.admin_email, self.hashed_pw))
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")
            await db.commit()