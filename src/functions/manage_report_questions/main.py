import json
import logging
from router import route_request

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        path = event.get('rawPath', '') or event.get("path", "")
        method = event.get('httpMethod', 'POST')
        body = event.get('body', '{}')
        params = event.get('queryStringParameters', {})

        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body
        
        status_code, response_body = route_request(path, method, payload, params)
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"Error with lambda event: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Invalid JSON in request body: {str(e)}'})
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