from dataclasses import dataclass

from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from common.emails import EmailService
from common.auth import pw_hasher
import secrets
from datetime import datetime, timezone, timedelta
import logging


@dataclass
class SendEmailVerificationCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper: DBWrapper, email_service: EmailService):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT email, email_confirmed FROM user_auth WHERE user_id = :user_id", {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                user_email, email_confirmed = row
            if bool(email_confirmed):
                raise Problem("User's email is already confirmed", status=400)
            token_id = secrets.token_hex(16)
            expires_on = int((datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp())
            await db.execute("INSERT INTO email_verifications(token_id, user_id, expires_on) VALUES(:token_id, :user_id, :expires_on)",
                             {"token_id": token_id, "user_id": self.user_id, "expires_on": expires_on})
            await db.commit()

        subject = "Email Confirmation - MKCentral"
        content = f'Welcome to MKCentral! Click the link below to confirm your email address.\
                    \nThis link will expire in 60 minutes.\
                    \n<a href="{email_service.site_url}/user/confirm-email?token={token_id}">Confirm Email</a>'
        await email_service.send_email(user_email, subject, content)

@dataclass
class ChangeEmailCommand(Command[None]):
    user_id: int
    new_email: str
    password: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT password_hash FROM user_auth WHERE user_id = :user_id", {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                password_hash = row[0]
            try:
                pw_hasher.verify(password_hash, self.password)
            except:
                raise Problem("Password is incorrect", status=401)
            async with db.execute("SELECT email FROM user_auth WHERE email = :new_email AND user_id != :user_id", {"new_email": self.new_email, "user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Email is used by another user", status=400)
            await db.execute("UPDATE user_auth SET email = :new_email, email_confirmed = 0 WHERE user_id = :user_id", {"new_email": self.new_email, "user_id": self.user_id})
            await db.commit()

@dataclass
class VerifyEmailCommand(Command[None]):
    token_id: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT user_id FROM email_verifications WHERE token_id = :token_id", {"token_id": self.token_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired", status=400)
                user_id = row[0]
            await db.execute("DELETE FROM email_verifications WHERE token_id = :token_id", {"token_id": self.token_id})
            await db.execute("UPDATE user_auth SET email_confirmed = 1 WHERE user_id = :user_id", {"user_id": user_id})
            await db.commit()


@dataclass
class SendPasswordResetEmailCommand(Command[None]):
    user_email: str

    async def handle(self, db_wrapper: DBWrapper, email_service: EmailService):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT user_id FROM user_auth WHERE email = :user_email", {"user_email": self.user_email}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    # Don't reveal if email exists or not
                    logging.info(f"Password reset requested for non-existent email: {self.user_email}")
                    return # Silently fail
                user_id = row[0]
            token_id = secrets.token_hex(16)
            expires_on = int((datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp())
            await db.execute("INSERT INTO password_resets(token_id, user_id, expires_on) VALUES(:token_id, :user_id, :expires_on)",
                             {"token_id": token_id, "user_id": user_id, "expires_on": expires_on})
            await db.commit()
        subject = "Password Reset - MKCentral"
        content = f'You requested a password reset on MKCentral. You can reset your password by clicking the link below (expires in 60 minutes): \
            \n<a href="{email_service.site_url}/user/reset-password?token={token_id}">Reset Password</a>'
        await email_service.send_email(self.user_email, subject, content)

@dataclass
class SendPasswordResetToPlayerCommand(Command[None]):
    player_id: int

    async def handle(self, db_wrapper: DBWrapper, email_service: EmailService):
        async with db_wrapper.connect(db_name='main', attach=['auth']) as db:
            async with db.execute("""SELECT u.id, ua.email
                                    FROM users u
                                    JOIN auth.user_auth ua ON u.id = ua.user_id
                                    WHERE u.player_id = ?""", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("User not found", status=404)
                user_id, user_email = row
            token_id = secrets.token_hex(16)
            expires_on = int((datetime.now(timezone.utc) + timedelta(minutes=60)).timestamp())
            await db.execute("INSERT INTO password_resets(token_id, user_id, expires_on) VALUES(:token_id, :user_id, :expires_on)",
                             {"token_id": token_id, "user_id": user_id, "expires_on": expires_on})
            await db.commit()
            
        subject = "Password Reset - MKCentral"
        content = f'You requested a password reset on MKCentral. You can reset your password by clicking the link below (expires in 60 minutes): \
            \n<a href="{email_service.site_url}/user/reset-password?token={token_id}">Reset Password</a>'
        await email_service.send_email(user_email, subject, content)


@dataclass
class GetUserInfoFromPasswordResetTokenCommand(Command[UserInfo]):
    token_id: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='main', attach=['auth'], readonly=True) as db:
            query = """
                SELECT ua.user_id, ua.email, u.join_date, ua.email_confirmed, ua.force_password_reset
                FROM auth.password_resets p
                JOIN auth.user_auth ua ON p.user_id = ua.user_id
                JOIN users u ON ua.user_id = u.id
                WHERE p.token_id = :token_id
            """
            async with db.execute(query, {"token_id": self.token_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired or invalid", status=400)
                user_id, email, join_date, email_confirmed, force_password_reset = row

        # Player info is not needed for password reset context, so pass None
        return UserInfo(user_id, email, join_date, bool(email_confirmed), bool(force_password_reset), player=None)


@dataclass
class ResetPasswordWithTokenCommand(Command[None]):
    token_id: str
    new_password_hash: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT user_id FROM password_resets WHERE token_id = :token_id", {"token_id": self.token_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Token is expired", status=400)
                user_id = row[0]
            await db.execute("DELETE FROM password_resets WHERE token_id = :token_id", {"token_id": self.token_id})
            await db.execute("UPDATE user_auth SET password_hash = :new_password_hash, force_password_reset = 0 WHERE user_id = :user_id", {"new_password_hash": self.new_password_hash, "user_id": user_id})
            await db.commit()


@dataclass
class ResetPasswordCommand(Command[None]):
    user_id: int
    old_password: str
    new_password_hash: str

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='auth') as db:
            async with db.execute("SELECT password_hash FROM user_auth WHERE user_id = :user_id", {"user_id": self.user_id}) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                correct_old_pw_hash = row[0]
                try:
                    pw_hasher.verify(correct_old_pw_hash, self.old_password)
                except:
                    raise Problem("Old password is incorrect", status=401)
            await db.execute("UPDATE user_auth SET password_hash = :new_password_hash, force_password_reset = 0 WHERE user_id = :user_id", {"new_password_hash": self.new_password_hash, "user_id": self.user_id})
            await db.commit()


@dataclass
class RemoveExpiredTokensCommand(Command[None]):
    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='auth') as db:
            now = int(datetime.now(timezone.utc).timestamp())
            await db.execute("DELETE FROM email_verifications WHERE expires_on < :now", {"now": now})
            await db.execute("DELETE FROM password_resets WHERE expires_on < :now", {"now": now})
            await db.commit()
