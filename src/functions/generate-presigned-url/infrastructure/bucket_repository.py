import boto3
import logging
from botocore.exceptions import ClientError
from botocore.client import Config
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class S3Client:
    def __init__(self):
        s3_params = {
            "service_name": "s3",
            "region_name": "sa-east-1",
            "config": Config(signature_version='s3v4')
        }

        if settings.BUCKET_ENDPOINT:
            s3_params["endpoint_url"] = settings.BUCKET_ENDPOINT

        self.s3 = boto3.client(**s3_params)


    def presigned_url(self, object_key: str):
        try:
            if not settings.S3_INPUT_BUCKET_NAME:
                raise ValueError("Missing required environment variable: S3_INPUT_BUCKET_NAME")

            response = self.s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.S3_INPUT_BUCKET_NAME,
                    'Key': object_key
                },
                ExpiresIn=300,
                HttpMethod='PUT'
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while generating presigned URL: {e}.",
                exc_info=True,
                extra={"bucket_name": settings.S3_INPUT_BUCKET_NAME, "file_key": object_key}
            )
            raise

        return {
            "upload_url": response,
            "file_key": object_key,
        }
