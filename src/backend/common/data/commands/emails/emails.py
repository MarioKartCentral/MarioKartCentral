from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
from common.auth import pw_hasher
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
    site_url: str
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
        content = f"Welcome to Mario Kart Central! Click the link below to confirm your email address.\
                    \nThis link will expire in 60 minutes.\
                    \n{self.site_url}/user/confirm-email?token={token_id}"
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

@dataclass
class SendPasswordResetEmailCommand(Command[None]):
    user_email: str
    site_url: str
    from_email: str
    hostname: str
    port: int
    username: str | None
    password: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM users WHERE email = ?", (self.user_email,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                user_id = row[0]
            token_id = secrets.token_hex(16)
            expires_on = int((datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp())
            await db.execute("INSERT INTO password_resets(token_id, user_id, expires_on) VALUES(?, ?, ?)",
                             (token_id, user_id, expires_on))
            await db.commit()
        subject = "Password Reset - Mario Kart Central"
        content = f"You requested a password reset on Mario Kart Central. You can reset your password by clicking the link below (expires in 60 minutes): \
            \n{self.site_url}/user/reset-password?token={token_id}"
        await send_email(self.from_email, self.user_email, subject, content, self.hostname, self.port, self.username, self.password)

@dataclass
class GetUserInfoFromPasswordResetTokenCommand(Command[UserInfo]):
    token_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT u.id, u.email, u.join_date, u.email_confirmed, u.force_password_reset FROM users u
                                    JOIN password_resets p ON u.id = p.user_id
                                    WHERE p.token_id = ?""", (self.token_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired", status=400)
                user_id, email, join_date, email_confirmed, force_password_reset = row
                user = UserInfo(user_id, email, join_date, bool(email_confirmed), bool(force_password_reset), None)
                return user

@dataclass
class ResetPasswordWithTokenCommand(Command[None]):
    token_id: str
    new_password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM password_resets WHERE token_id = ?", (self.token_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired", status=400)
                user_id = row[0]
            await db.execute("DELETE FROM password_resets WHERE token_id = ?", (self.token_id,))
            await db.execute("UPDATE users SET password_hash = ?, force_password_reset = 0 WHERE id = ?", (self.new_password_hash, user_id))
            await db.commit()

@dataclass
class ResetPasswordCommand(Command[None]):
    user_id: int
    old_password: str
    new_password_hash: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT password_hash FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                correct_old_pw_hash = row[0]
                try:
                    pw_hasher.verify(correct_old_pw_hash, self.old_password)
                except:
                    raise Problem("Old password is incorrect", status=401)
            await db.execute("UPDATE users SET password_hash = ?, force_password_reset = 0 WHERE id = ?", (self.new_password_hash, self.user_id))
            await db.commit()

@dataclass
class RemoveExpiredTokensCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            now = int(datetime.now(timezone.utc).timestamp())
            await db.execute("DELETE FROM email_verifications WHERE expires_on < ?", (now,))
            await db.execute("DELETE FROM password_resets WHERE expires_on < ?", (now,))
            await db.commit()