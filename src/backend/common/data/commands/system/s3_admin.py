from common.data.command import Command
from common.data import s3
from common.data.s3 import S3Wrapper


class InitializeS3BucketsCommand(Command[None]):
    async def handle(self, s3_wrapper: S3Wrapper):
        bucket_names = await s3_wrapper.list_buckets()

        # all buckets we need for the API to run
        api_buckets = [
            s3.TOURNAMENTS_BUCKET, s3.SERIES_BUCKET, s3.TEMPLATES_BUCKET, s3.MKCV1_BUCKET, s3.FINGERPRINT_BUCKET, 
            s3.POST_BUCKET, s3.IMAGE_BUCKET, s3.DB_BACKUP_BUCKET
        ]
        
        for bucket in api_buckets:
            if bucket not in bucket_names:
                await s3_wrapper.create_bucket(bucket)