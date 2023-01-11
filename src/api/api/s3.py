import aiobotocore.session
from api import settings

def create_s3_client(session: aiobotocore.session.AioSession):
    return session.create_client(
        's3',
        aws_secret_access_key=str(settings.AWS_SECRET_ACCESS_KEY),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        endpoint_url=settings.AWS_ENDPOINT_URL)

async def init_s3():
    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        resp = await s3_client.list_buckets()
        # names of currently existing buckets in s3
        bucket_names = [b['Name'] for b in resp['Buckets']]
        # all buckets we need for the API to run
        api_buckets = ['tournaments', 'series']
        # create buckets if they can't be found in s3
        for bucket in api_buckets:
            if bucket not in bucket_names:
                result = await s3_client.create_bucket(Bucket=bucket)