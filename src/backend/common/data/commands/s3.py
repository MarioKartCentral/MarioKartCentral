
from dataclasses import dataclass
from common.data.commands import Command
import common.data.s3 as s3


class InitializeS3BucketsCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        bucket_names = await s3_wrapper.list_buckets()

        # all buckets we need for the API to run
        api_buckets = [s3.TOURNAMENTS, s3.SERIES, s3.TEMPLATES, s3.COMMAND_LOG]
        for bucket in api_buckets:
            if bucket not in bucket_names:
                await s3_wrapper.create_bucket(bucket)

@dataclass
class ReadFileInS3BucketCommand(Command[bytes | None]):
    bucket: str
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        return await s3_wrapper.get_object(self.bucket, self.file_name)

@dataclass
class WriteMessageToFileInS3BucketCommand(Command[None]):
    bucket: str
    file_name: str
    message: bytes

    async def handle(self, db_wrapper, s3_wrapper):
        await s3_wrapper.put_object(self.bucket, self.file_name, self.message)