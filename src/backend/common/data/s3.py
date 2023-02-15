import aiobotocore.session

class S3Wrapper():
    def __init__(self, aws_secret_access_key, aws_access_key_id, aws_endpoint_url):
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_access_key_id = aws_access_key_id
        self.aws_endpoint_url = aws_endpoint_url

    def create_client(self, session: aiobotocore.session.AioSession):
        return session.create_client(
            's3',
            aws_secret_access_key=str(self.aws_secret_access_key),
            aws_access_key_id=self.aws_access_key_id,
            endpoint_url=self.aws_endpoint_url)

    async def init(self):
        session = aiobotocore.session.get_session()
        async with self.create_client(session) as s3_client:
            resp = await s3_client.list_buckets()
            # names of currently existing buckets in s3
            bucket_names = [b['Name'] for b in resp['Buckets']]
            # all buckets we need for the API to run
            api_buckets = ['tournaments', 'series', 'templates']
            # create buckets if they can't be found in s3
            for bucket in api_buckets:
                if bucket not in bucket_names:
                    result = await s3_client.create_bucket(Bucket=bucket)