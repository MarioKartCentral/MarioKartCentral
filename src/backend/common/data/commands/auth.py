
from dataclasses import dataclass
from common.auth import roles
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, User

@dataclass 
class GetUserIdFromSessionCommand(Command[User | None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            user_id = int(row[0])
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
            
            return User(user_id, player_id)

@dataclass
class GetUserWithPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                JOIN sessions s on s.user_id = u.id
                JOIN role_permissions rp on rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ?
                LIMIT 1""", (self.session_id, self.permission_name)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            return User(int(row[0]), row[1])
        
@dataclass
class GetUserWithTeamPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str
    team_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM roles r
                JOIN user_team_roles ur ON ur.role_id = r.id
                JOIN users u ON ur.user_id = u.id
                JOIN sessions s ON s.user_id = u.id
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ? AND ur.team_id = ?
                LIMIT 1""", (self.session_id, self.permission_name, self.team_id)) as cursor:
                row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return User(int(row[0]), row[1])
        
@dataclass
class CheckPermissionsCommand(Command[list[str]]):
    user_id: int
    permissions: list[str]

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(f"""
                SELECT DISTINCT p.name
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ? AND p.name IN ({','.join([f"'{p}'" for p in self.permissions])})
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])
        
@dataclass
class CreateSessionCommand(Command[None]):
    session_id: str
    user_id: int
    expires_on: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            command = "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)"
            async with db.execute(command, (self.session_id, self.user_id, self.expires_on)) as cursor:
                rows_inserted = cursor.rowcount

            # TODO: Run queries to identify why session creation failed
            if rows_inserted != 1:
                raise Problem("Failed to create session")
                
            await db.commit()
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))
            await db.commit()

@save_to_command_log
@dataclass
class GrantRoleCommand(Command[None]):
    granter_user_id: int
    target_user_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        # For now, the rules about which roles can grant other roles is defined here, but we could move it to  the database
        # in the future.
        if self.role in [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]:
            allowed_roles = [roles.SUPER_ADMINISTRATOR]
        else:
            allowed_roles = [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]

        allowed_role_ids = [roles.id_by_default_role[role] for role in allowed_roles]

        async with db_wrapper.connect() as db:
            async with db.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    JOIN users u on ur.user_id = u.id
                    WHERE u.id = ? AND r.id IN ({','.join(map(str, allowed_role_ids))})
                )""", (self.granter_user_id,)) as cursor:
                row = await cursor.fetchone()
                can_grant = row is not None and bool(row[0])

            if not can_grant:
                raise Problem("Not authorized to grant role", status=401)

            try:
                async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                    row = await cursor.fetchone()
                    role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)

                await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)", (self.target_user_id, role_id))
                await db.commit()
            except Exception:
                async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (self.target_user_id,)) as cursor:
                    row = await cursor.fetchone()
                    user_exists = row is not None

                if not user_exists:
                    raise Problem("User not found", status=404)
                else:
                    raise Problem("Unexpected error")