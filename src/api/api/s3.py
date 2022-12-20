import aiobotocore.session
from api import settings

def create_s3_client(session: aiobotocore.session.AioSession):
    return session.create_client(
        's3',
        aws_secret_access_key=str(settings.AWS_SECRET_ACCESS_KEY),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        endpoint_url=settings.AWS_ENDPOINT_URL)