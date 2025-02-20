from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
from datetime import datetime, timezone
import secrets

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
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])

@dataclass
class CreateSessionCommand(Command[SessionInfo]):
    user_id: int
    ip_address: str | None
    persistent_session_id: str | None
    fingerprint: Fingerprint

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            session_id = secrets.token_hex(16)
            max_age = timedelta(days=365)
            current_date = datetime.now(timezone.utc)
            expiration_date = current_date + max_age

            persistent_session_id = self.persistent_session_id
            if not persistent_session_id:
                persistent_session_id = secrets.token_hex(16)
            current_timestamp = int(current_date.timestamp())
            had_persistent_session = self.persistent_session_id is not None
            ip = self.ip_address if self.ip_address else "0.0.0.0"

            command = "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)"
            async with db.execute(command, (session_id, self.user_id, int(expiration_date.timestamp()))) as cursor:
                rows_inserted = cursor.rowcount

            # TODO: Run queries to identify why session creation failed
            if rows_inserted != 1:
                raise Problem("Failed to create session")
            
            await db.execute("""INSERT INTO user_logins(user_id, ip, session_id, persistent_session_id, fingerprint, had_persistent_session, date)
                                VALUES(?, ?, ?, ?, ?, ?, ?)""", (self.user_id, ip, session_id, persistent_session_id, self.fingerprint.hash,
                                                                 had_persistent_session, current_timestamp))
                
            await db.commit()
            return SessionInfo(session_id, persistent_session_id, max_age)
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            now = int(datetime.now(timezone.utc).timestamp())
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))
            await db.execute("UPDATE user_logins SET logout_date = ? WHERE session_id = ?", (now, self.session_id))
            await db.commit()