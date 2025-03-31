from dataclasses import dataclass

from types_aiobotocore_ses import SESClient
from common.data.commands import Command
from common.data.models import *
from common.auth import pw_hasher
import aiosmtplib
from email.message import EmailMessage
import secrets
from datetime import datetime, timezone, timedelta
import aiobotocore.session
import html


async def send_email(to_email: str, subject: str, content: str, config: EmailServiceConfig):
    """
    Send email using either SMTP or Amazon SES based on configuration.
    
    If config.use_ses is True, AWS SES will be used. Otherwise, SMTP will be used.
    """
    message = EmailMessage()
    message["From"] = config.from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)
    
    if config.use_ses and config.ses_config:
        session = aiobotocore.session.get_session()
        client: SESClient
        async with session.create_client('ses', # type: ignore
                                         region_name=config.ses_config.region,
                                         aws_access_key_id=config.ses_config.access_key_id,
                                         aws_secret_access_key=config.ses_config.secret_access_key) as client:         
            await client.send_email(
                Source=config.from_email,
                Destination={ 'ToAddresses': [to_email] },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': content,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': html.escape(content).replace('\n', '<br>'),
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
    elif config.smtp_config:
        await aiosmtplib.send(message, hostname=config.smtp_config.hostname, port=config.smtp_config.port)
    else:
        raise ValueError("Neither SES nor SMTP configuration is complete. Please provide either valid SES or SMTP settings.")


@dataclass
class SendEmailVerificationCommand(Command[None]):
    user_id: int
    email_config: EmailServiceConfig

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
                    \n{self.email_config.site_url}/user/confirm-email?token={token_id}"
        await send_email(user_email, subject, content, self.email_config)


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
    email_config: EmailServiceConfig

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
            \n{self.email_config.site_url}/user/reset-password?token={token_id}"
        await send_email(self.user_email, subject, content, self.email_config)


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
                user = UserInfo(user_id, email, join_date, bool(
                    email_confirmed), bool(force_password_reset), None)
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
