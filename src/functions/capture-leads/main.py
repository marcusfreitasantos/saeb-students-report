import json
import logging

from infrastructure.dynamodb_repository import DynamoDBClient
from services.lead_controller import LeadController

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        body = event.get("body") or {}

        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body

        dynamodb_client = DynamoDBClient()
        lead_controller = LeadController(dynamodb_client=dynamodb_client)
        status_code, response_body = lead_controller.create(payload)

        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body),
        }
    except json.JSONDecodeError as e:
        logger.error(f"Error with lambda event: {str(e)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Invalid JSON in request body: {str(e)}"}),
        }
    except Exception as e:
        logger.error(f"Error with lambda event: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
