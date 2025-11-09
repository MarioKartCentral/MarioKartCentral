
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiobotocore.session
import aiosmtplib


class EmailService(ABC):
    def __init__(self, from_email: str, site_url: str):
        self.from_email = from_email
        self.site_url = site_url

    @abstractmethod
    async def send_email(self, to_email: str, subject: str, content: str) -> None:
        pass

class SMTPEmailService(EmailService):
    def __init__(self, from_email: str, site_url: str, hostname: str, port: int):
        super().__init__(from_email, site_url)
        self.hostname = hostname
        self.port = port

    async def send_email(self, to_email: str, subject: str, content: str) -> None:
        message = MIMEMultipart("alternative")
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        html_message = MIMEText(content, "html", "utf-8")
        message.attach(html_message)
        await aiosmtplib.send(message, hostname=self.hostname, port=self.port)

class SESEmailService(EmailService):
    def __init__(self, from_email: str, site_url: str, access_key_id: str, secret_access_key: str, region: str):
        super().__init__(from_email, site_url)
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region

    async def send_email(self, to_email: str, subject: str, content: str) -> None:
        session = aiobotocore.session.get_session()
        async with session.create_client( # pyright: ignore[reportUnknownMemberType]
            service_name='ses',
            region_name=self.region,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        ) as client:
            await client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {
                            'Data': content.replace('\n', '<br>'),
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )