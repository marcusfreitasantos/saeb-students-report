import json
import logging
from infrastructure.dynamodb_repository import DynamoDBClient
from infrastructure.bucket_repository import S3Client
from infrastructure.sqs_repository import SQSClient
from services.event_controller import EventController

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def response_body(data):
    if hasattr(data, "to_dict"):
        return data.to_dict()

    return data

def handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        db_client = DynamoDBClient()
        s3_client = S3Client()
        sqs_client = SQSClient()

        event_controller = EventController(event=event, db_client=db_client, s3_client=s3_client, sqs_client=sqs_client)
        result = event_controller.handle(event)

        logger.info(f"Generate report result: {json.dumps(response_body(result))}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body(result))
        }

    except Exception as e:
        logger.error(f"Error with lambda event: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }


if __name__ == "__main__":
    handler()
