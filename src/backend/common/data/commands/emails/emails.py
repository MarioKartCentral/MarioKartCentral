from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
import aiosmtplib
from email.message import EmailMessage
import secrets
from datetime import datetime, timezone, timedelta

async def send_email(from_email: str, to_email: str, subject: str, content: str,
                     hostname: str, port: int, username: str | None, password: str | None):
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)
    await aiosmtplib.send(message, hostname=hostname, port=port, username=username, password=password)

@dataclass
class SendEmailVerificationCommand(Command[None]):
    user_id: int
    from_email: str
    hostname: str
    port: int
    username: str | None
    password: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT email, email_confirmed FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                user_email, email_confirmed = row
            if bool(email_confirmed):
                raise Problem("User's email is already confirmed", status=400)
            token_id = secrets.token_hex(16)
            expires_on = int((datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp())
            await db.execute("INSERT INTO email_verifications(token_id, user_id, expires_on) VALUES(?, ?, ?)",
                             (token_id, self.user_id, expires_on))
            await db.commit()

        subject = "Email Confirmation - Mario Kart Central"
        content = f"Confirmation token: {token_id}"
        await send_email(self.from_email, user_email, subject, content, self.hostname, self.port, self.username, self.password)

@dataclass
class VerifyEmailCommand(Command[None]):
    token_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM email_verifications WHERE token_id = ?", (self.token_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired", status=400)
                user_id = row[0]
            await db.execute("DELETE FROM email_verifications WHERE token_id = ?", (self.token_id,))
            await db.execute("UPDATE users SET email_confirmed = 1 WHERE id = ?", (user_id,))
            await db.commit()