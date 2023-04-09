from dataclasses import dataclass
import aiobotocore.session
from types_aiobotocore_s3 import S3Client

@dataclass
class S3Wrapper:
    client: S3Client

    async def create_bucket(self, bucket_name: str):
        await self.client.create_bucket(Bucket=bucket_name)

    async def list_buckets(self):
        buckets = await self.client.list_buckets()
        return [b['Name'] for b in buckets['Buckets'] if 'Name' in b]

    async def get_object(self, bucket_name: str, key: str):
        try:
            response = await self.client.get_object(Bucket=bucket_name, Key=key)
            async with response["Body"] as stream:
                return await stream.read()
        except self.client.exceptions.NoSuchKey:
            return None

    async def put_object(self, bucket_name: str, key: str, body: bytes):
        await self.client.put_object(Bucket=bucket_name, Key=key, Body=body)

@dataclass
class S3WrapperManager:
    aws_secret_access_key: str
    aws_access_key_id: str
    aws_endpoint_url: str
    client: S3Client | None = None

    async def __aenter__(self) -> S3Wrapper:
        session = aiobotocore.session.get_session()
        self.client = await session.create_client(
            's3',
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id,
            endpoint_url=self.aws_endpoint_url).__aenter__()
        return S3Wrapper(self.client)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
        self.client = None