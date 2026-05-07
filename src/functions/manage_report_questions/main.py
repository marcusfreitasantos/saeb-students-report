import json
from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController

def route_request(path, method, payload):
    dynamodb_client = DynamoDBClient()

    if path == '/questions/create' and method == 'POST':
        questions_batch = payload.get('questions_batch', [])
        if not questions_batch:
            return 400, {'error': 'questions_batch is required'}
        
        question_controller = QuestionController(questions_batch, dynamodb_client)
        result = question_controller.batch_create()
        return 200, {'success': True, 'message': result}
    
    elif path == '/interventions/create' and method == 'POST':
        interventions_batch = payload.get('interventions_batch', [])
        if not interventions_batch:
            return 400, {'error': 'interventions_batch is required'}
        result = "Intervention batch processing not yet implemented"
        return 200, {'success': True, 'message': result}
    
    else:
        return 404, {'error': f'Route {method} {path} not found'}


def handler(event, context):
    try:
        # Extract request information
        path = event.get('requestContext', {}).get('resourcePath', '')
        method = event.get('httpMethod', 'POST')
        body = event.get('body', '{}')
        
        # Parse body
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body
        
        # Route to appropriate handler
        status_code, response_body = route_request(path, method, payload)
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }
    
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Invalid JSON in request body: {str(e)}'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
    

if __name__ == "__main__":
    handler()