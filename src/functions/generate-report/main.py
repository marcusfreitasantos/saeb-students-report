import json
import logging
from services.event_controller  import EventController
from infrastructure.dynamodb_repository import DynamoDBClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def handler(event, context):
    try:        
        logger.info(f"Received event: {json.dumps(event)}")
        db_client = DynamoDBClient()
        event_controller = EventController(event_data=event, db_client=db_client)
        
        created_event = event_controller.create(event, "STARTED", "")

        logger.info(f"Created event: {json.dumps(created_event.to_dict())}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(created_event.to_dict())
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