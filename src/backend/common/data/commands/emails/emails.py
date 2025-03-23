from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *
import aiosmtplib
from email.message import EmailMessage

async def send_email(from_email: str, to_email: str, subject: str, content: str,
                     hostname: str, port: int, username: str | None, password: str | None):
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)
    await aiosmtplib.send(message, hostname=hostname, port=port, username=username, password=password)

@dataclass
class SendEmailCommand(Command[None]):
    from_email: str
    hostname: str
    port: int
    username: str | None
    password: str | None
    
    async def handle(self, db_wrapper, s3_wrapper):
        to_email = "test2@test.com"
        subject = "testing!!"
        content = "hey there lol"
        await send_email(self.from_email, to_email, subject, content, self.hostname, self.port, self.username, self.password)