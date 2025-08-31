from dataclasses import dataclass
from typing import Dict
from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from datetime import datetime, timezone, timedelta
import secrets

@dataclass 
class GetUserIdFromSessionCommand(Command[User | None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='main', attach=['sessions'], readonly=True) as db:
            query = """
                SELECT s.user_id, u.player_id 
                FROM sessions.sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_id = :session_id
            """
            async with db.execute(query, {"session_id": self.session_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                user_id, player_id = row
                return User(user_id, player_id)

@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='sessions', readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])

@dataclass
class CreateSessionCommand(Command[SessionInfo]):
    user_id: int
    ip_address: str | None
    persistent_session_id: str | None
    fingerprint: Fingerprint

    async def handle(self, db_wrapper: DBWrapper):
        session_id = secrets.token_hex(16)
        max_age = timedelta(days=365)
        current_date = datetime.now(timezone.utc)
        expiration_date = current_date + max_age
        current_timestamp = int(current_date.timestamp())

        persistent_session_id = self.persistent_session_id or secrets.token_hex(16)
        had_persistent_session = self.persistent_session_id is not None
        ip = self.ip_address or "0.0.0.0"

        async with db_wrapper.connect(db_name='sessions') as db:
            session_command = """
                INSERT INTO sessions(session_id, user_id, expires_on) 
                VALUES (:session_id, :user_id, :expires_on)
            """
            session_params: Dict[str, Any] = {
                "session_id": session_id, 
                "user_id": self.user_id, 
                "expires_on": int(expiration_date.timestamp())
            }
            async with db.execute(session_command, session_params) as cursor:
                if cursor.rowcount != 1:
                    raise Problem("Failed to create session")
            await db.commit()
        
        async with db_wrapper.connect(db_name='user_activity') as db:
            ip_query_command = """
                SELECT id FROM ip_addresses WHERE ip_address = :ip
            """
            ip_address_id = None
            async with db.execute(ip_query_command, {"ip": ip}) as cursor:
                row = await cursor.fetchone()
                if row:
                    ip_address_id = row[0]
            
            if ip_address_id is None:
                ip_insert_command = """
                    INSERT INTO ip_addresses(ip_address, is_mobile, is_vpn, is_checked)
                    VALUES(:ip, 0, 0, 0)
                """
                async with db.execute(ip_insert_command, {"ip": ip}) as cursor:
                    if cursor.rowcount != 1:
                        raise Problem("Failed to insert IP address")
                    
                    ip_address_id = cursor.lastrowid
                await db.commit()
                
            login_command = """
                INSERT INTO user_logins(user_id, ip_address_id, session_id, persistent_session_id, fingerprint, had_persistent_session, date)
                VALUES(:user_id, :ip_address_id, :session_id, :persistent_session_id, :fingerprint, :had_persistent_session, :date)
            """
            login_params: Dict[str, Any] = {
                "user_id": self.user_id, 
                "ip_address_id": ip_address_id, 
                "session_id": session_id, 
                "persistent_session_id": persistent_session_id, 
                "fingerprint": self.fingerprint.hash,
                "had_persistent_session": had_persistent_session, 
                "date": current_timestamp
            }
            await db.execute(login_command, login_params)
            await db.commit()
            
        return SessionInfo(session_id, persistent_session_id, max_age)

@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper: DBWrapper):
        now = int(datetime.now(timezone.utc).timestamp())
        
        async with db_wrapper.connect(db_name='sessions') as db:
            await db.execute("DELETE FROM sessions WHERE session_id = :session_id", {"session_id": self.session_id})
            await db.commit()
        
        async with db_wrapper.connect(db_name='user_activity') as db:
            await db.execute("UPDATE user_logins SET logout_date = :now WHERE session_id = :session_id", {"now": now, "session_id": self.session_id})
            await db.commit()