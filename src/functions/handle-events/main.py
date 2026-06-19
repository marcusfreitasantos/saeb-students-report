import json
import logging
from services.event_controller  import EventController
from infrastructure.dynamodb_repository import DynamoDBClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def is_s3_event(event):
    records = event.get("Records", [])
    return bool(records and records[0].get("eventSource") == "aws:s3")


def is_http_get_event(event):
    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})
    return http_context.get("method") == "GET"


def get_filekey_from_http_event(event):
    params = event.get("queryStringParameters") or {}
    filekey = params.get("filekey")

    if not filekey:
        raise ValueError("Missing required query parameter: filekey")

    return filekey


def response_body(data):
    if hasattr(data, "to_dict"):
        return data.to_dict()

    return data


def handler(event, context):
    try:        
        db_client = DynamoDBClient()
        event_controller = EventController(event_data=event, db_client=db_client)

        if is_s3_event(event):
            result = event_controller.handle(event)
        elif is_http_get_event(event):
            filekey = get_filekey_from_http_event(event)
            result = event_controller.get_item(filekey)
        else:
            raise ValueError("Unsupported event source")
        
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
