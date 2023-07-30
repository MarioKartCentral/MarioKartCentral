from dataclasses import dataclass
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, User, UserLoginData


@dataclass
class GetUserDataFromEmailCommand(Command[UserLoginData | None]):
    email: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id, password_hash FROM users WHERE email = ?", (self.email, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return UserLoginData(int(row[0]), row[1], self.email, str(row[2]))

@dataclass
class GetUserDataFromIdCommand(Command[User | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id, player_id FROM users WHERE id = ?", (self.id, )) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None
            
            return User(int(row[0]), row[1])
            
@save_to_command_log     
@dataclass
class CreateUserCommand(Command[User]):
    email: str
    password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            row = await db.execute_insert("INSERT INTO users(email, password_hash) VALUES (?, ?)", (self.email, self.password_hash))

            # TODO: Run queries to identify why user creation failed
            if row is None:
                raise Problem("Failed to create user")

            await db.commit()
            return User(int(row[0]), None)
        
@dataclass
class GetPlayerIdForUserCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> int:
        async with db_wrapper.connect(readonly=True) as db:
            # get player id from user id in request
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("User does not exist", status=404)

                return int(row[0])