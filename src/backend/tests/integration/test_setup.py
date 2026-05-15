import pytest
from common.data.commands import InitializeS3BucketsCommand
from common.data.s3 import S3WrapperManager
from common.data.db import DBWrapper


@pytest.mark.asyncio
@pytest.mark.parametrize("bucket_name", [
    "mkc-tournaments",
    "mkc-templates",
    "mkc-series",
    "mkc-v1data",
    "mkc-posts",
    "mkc-fingerprints",
    "mkc-img",
    "mkc-db-backups"
])
async def test_initialise_s3_buckets_command(mocked_s3_manager: S3WrapperManager, bucket_name: str):
    async with mocked_s3_manager as s3_wrapper:
        await InitializeS3BucketsCommand().handle(s3_wrapper)
        bucket_list = await s3_wrapper.list_buckets()
        assert bucket_name in bucket_list


def test_unknown_db_reset_raises_error(test_db: DBWrapper):
    with pytest.raises(ValueError) as exception:
        test_db.reset_db('unknown')
        assert str(
            exception.value) == "Database 'unknown' not configured for reset."
