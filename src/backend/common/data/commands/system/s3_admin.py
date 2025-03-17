from common.data.commands import Command
import common.data.s3 as s3


class InitializeS3BucketsCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        bucket_names = await s3_wrapper.list_buckets()

        # all buckets we need for the API to run
        api_buckets = [s3.TOURNAMENTS_BUCKET, s3.SERIES_BUCKET, s3.TEMPLATES_BUCKET, s3.COMMAND_LOG_BUCKET, s3.MKCV1_BUCKET, s3.POST_BUCKET]
        for bucket in api_buckets:
            if bucket not in bucket_names:
                await s3_wrapper.create_bucket(bucket)