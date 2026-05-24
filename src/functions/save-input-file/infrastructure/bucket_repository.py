import boto3
import logging
from botocore.exceptions import ClientError
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class S3Client:
    def __init__(self):
        s3_params = {
            "service_name": "s3",
            "region_name": "sa-east-1"
        }

        if settings.BUCKET_ENDPOINT:
            s3_params["endpoint_url"] = settings.BUCKET_ENDPOINT

        self.s3 = boto3.client(**s3_params)


    def presigned_url(self, file_key: str):
        try:
            response = self.s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.BUCKET_NAME,
                    'Key': file_key
                },
                ExpiresIn=300,
                HttpMethod='PUT'
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while generating presigned URL: {e}.",
                exc_info=True,
                extra={"bucket_name": settings.BUCKET_NAME, "file_key": file_key}
            )
            raise

        return {
            "upload_url": response,
            "file_key": file_key
        }