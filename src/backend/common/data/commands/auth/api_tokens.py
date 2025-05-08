from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
import secrets

@dataclass
class CreateAPITokenCommand(Command[None]):
    user_id: int
    mod_user_id: int
    name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name='main', attach=["auth"]) as db:
            exists_query = "SELECT EXISTS(SELECT 1 FROM users WHERE id = :user_id)"
            async with db.execute(exists_query, {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row or not row[0]:
                    raise Problem("User not found", status=404)
            # users should only be able to edit grant api tokens to users lower in the role hierarchy
            # than them. giving tokens to yourself is an exception, since you are the same level in the
            # role hierarchy as yourself
            if self.mod_user_id != self.user_id:
                perm_query = """
                    WITH mh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:mod_user_id),
                         uh AS (SELECT MIN(r.position) AS pos FROM roles r JOIN user_roles ur ON r.id=ur.role_id WHERE ur.user_id=:user_id)
                    SELECT EXISTS(SELECT 1 FROM mh JOIN uh WHERE uh.pos IS NULL OR mh.pos < uh.pos)
                """
                async with db.execute(perm_query, {"mod_user_id": self.mod_user_id, "user_id": self.user_id}) as cursor:
                    row = await cursor.fetchone()
                    if not row or not row[0]:
                        raise Problem("Cannot grant API tokens to users higher/equal in the role hierarchy to yourself", status=403)
            async with db.execute("SELECT name FROM auth.api_tokens WHERE user_id = ? AND name = ?", (self.user_id, self.name)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Token already exists with this name for this user", status=400)
            api_token = secrets.token_hex(16)
            await db.execute("INSERT INTO auth.api_tokens(token_id, user_id, name) VALUES(:token_id, :user_id, :name)", 
                             {"token_id": api_token, "user_id": self.user_id, "name": self.name})
            await db.commit()

@dataclass
class DeleteAPITokenCommand(Command[None]):
    token_id: str
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name="auth") as db:
            async with db.execute("SELECT token_id FROM api_tokens WHERE token_id = ? AND user_id = ?", (self.token_id, self.user_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token not found", status=404)
            await db.execute("DELETE FROM api_tokens WHERE token_id = ? AND user_id = ?", (self.token_id, self.user_id))
            await db.commit()

@dataclass
class GetUserFromAPITokenCommand(Command[User | None]):
    token_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name="main", attach=["auth"]) as db:
            async with db.execute("SELECT u.id, u.player_id FROM users u JOIN auth.api_tokens a ON u.id = a.user_id WHERE token_id = ?", (self.token_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                user_id, player_id = row
                return User(int(user_id), player_id)

@dataclass
class GetUserAPITokensCommand(Command[list[APIToken]]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(db_name="auth") as db:
            async with db.execute("SELECT token_id, user_id, name FROM api_tokens WHERE user_id = ?", (self.user_id,)) as cursor:
                rows = await cursor.fetchall()
                tokens: list[APIToken] = []
                for row in rows:
                    token_id, user_id, name = row
                    token = APIToken(int(user_id), token_id, name)
                    tokens.append(token)
                return tokens