from dataclasses import dataclass
from types import TracebackType
import aiobotocore.session
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_s3.literals import ObjectCannedACLType
from types_aiobotocore_s3.type_defs import ObjectTypeDef
from datetime import datetime

TOURNAMENTS_BUCKET = "mkc-tournaments"
TEMPLATES_BUCKET = "mkc-templates"
SERIES_BUCKET = "mkc-series"
MKCV1_BUCKET = "mkc-v1data"
POST_BUCKET = "mkc-posts"
FINGERPRINT_BUCKET = "mkc-fingerprints"
IMAGE_BUCKET = "mkc-img"
DB_BACKUP_BUCKET = "mkc-db-backups"

@dataclass
class S3Wrapper:
    _client: S3Client

    async def create_bucket(self, bucket_name: str):
        await self._client.create_bucket(Bucket=bucket_name)

    async def list_buckets(self) -> list[str]:
        buckets = await self._client.list_buckets()
        return [b['Name'] for b in buckets['Buckets'] if 'Name' in b]

    async def get_object(self, bucket_name: str, key: str):
        try:
            response = await self._client.get_object(Bucket=bucket_name, Key=key)
            async with response["Body"] as stream:
                return await stream.read()
        except self._client.exceptions.NoSuchKey:
            return None

    async def get_object_metadata_and_body(self, bucket_name: str, key: str) -> dict[str, object] | None:
        try:
            head_response = await self._client.head_object(Bucket=bucket_name, Key=key)
            last_modified: datetime = head_response['LastModified']

            get_response = await self._client.get_object(Bucket=bucket_name, Key=key)
            async with get_response["Body"] as stream:
                body = await stream.read()

            return {
                "LastModified": last_modified,
                "Body": body
            }

        except self._client.exceptions.NoSuchKey:
            return None
        except Exception:
            return None

    async def put_object(self, bucket_name: str, key: str, body: bytes, acl: ObjectCannedACLType = "private"):
        await self._client.put_object(Bucket=bucket_name, Key=key, Body=body, ACL=acl)

    async def list_objects(self, bucket_name: str) -> list[ObjectTypeDef]:
        """List objects in a bucket"""
        try:
            response = await self._client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                return response['Contents']
            return []
        except Exception:
            return []

    async def delete_object(self, bucket_name: str, key: str):
        await self._client.delete_object(Bucket=bucket_name, Key=key)

@dataclass
class S3WrapperManager:
    s3_secret_key: str
    s3_access_key: str
    s3_endpoint: str
    client: S3Client | None = None

    async def __aenter__(self) -> S3Wrapper:
        session = aiobotocore.session.get_session()
        self.client = await session.create_client( # pyright: ignore[reportUnknownMemberType]
            service_name='s3',
            aws_secret_access_key=self.s3_secret_key,
            aws_access_key_id=self.s3_access_key,
            endpoint_url=self.s3_endpoint).__aenter__()
        return S3Wrapper(self.client)

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        if self.client is not None:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
        self.client = None