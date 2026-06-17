import logging
from urllib.parse import quote

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from infrastructure.config.settings import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class S3Client:
    def __init__(self):
        s3_params = {
            "service_name": "s3",
            "region_name": settings.AWS_REGION,
            "config": Config(signature_version="s3v4"),
        }

        if settings.BUCKET_ENDPOINT:
            s3_params["endpoint_url"] = settings.BUCKET_ENDPOINT

        self.s3 = boto3.client(**s3_params)

    def get_file(self, filekey: str) -> bytes:
        bucket_name, object_key = self._bucket_and_key(filekey)

        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=object_key)
            return response["Body"].read()
        except ClientError as error:
            logger.error(
                "Error occurred while getting object from S3.",
                exc_info=True,
                extra={"bucket_name": bucket_name, "object_key": object_key},
            )
            raise error

    def put_file(
        self,
        bucket_name: str,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> None:
        try:
            self.s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=data,
                ContentType=content_type,
            )
        except ClientError as error:
            logger.error(
                "Error occurred while putting object into S3.",
                exc_info=True,
                extra={"bucket_name": bucket_name, "object_key": object_key},
            )
            raise error

    def download_url(self, bucket_name: str, object_key: str) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=3600,
            HttpMethod="GET",
        )

    def object_url(self, bucket_name: str, object_key: str) -> str:
        encoded_key = quote(object_key)
        if settings.BUCKET_ENDPOINT:
            return f"{settings.BUCKET_ENDPOINT.rstrip('/')}/{bucket_name}/{encoded_key}"

        return f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{encoded_key}"

    def _bucket_and_key(self, filekey: str) -> tuple[str, str]:
        if "/" in filekey:
            possible_bucket, object_key = filekey.split("/", 1)
            if possible_bucket:
                return possible_bucket, object_key

        return settings.S3_INPUT_BUCKET_NAME, filekey
