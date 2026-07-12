import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SQSClient:
    def __init__(self):
        sqs_params ={
            "service_name": "sqs",
            "region_name":  "sa-east-1",
        }

        if settings.SQS_ENDPOINT:
            sqs_params["endpoint_url"] = settings.SQS_ENDPOINT

        self.sqs = boto3.client(**sqs_params)
    

    def send_message(self, queue_url: str, message_body: str) -> None:
        try:
            self.sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
        except ClientError as error:
            logger.error(
                f"Error occurred while sending message to SQS: {error}. Queue URL: {queue_url}, Message Body: {message_body}",
                exc_info=True,
            )
            raise error
