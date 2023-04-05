from typing import Any
import aiobotocore.session

class S3Wrapper():
    def __init__(self, aws_secret_access_key, aws_access_key_id, aws_endpoint_url):
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_access_key_id = aws_access_key_id
        self.aws_endpoint_url = aws_endpoint_url

    # returning Any as the type hints in aiobotocore are broken
    def create_client(self, session: aiobotocore.session.AioSession) -> Any:
        return session.create_client(
            's3',
            aws_secret_access_key=str(self.aws_secret_access_key),
            aws_access_key_id=self.aws_access_key_id,
            endpoint_url=self.aws_endpoint_url)