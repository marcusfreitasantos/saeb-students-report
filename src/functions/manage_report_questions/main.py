import json
from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController
from services.intervention_controller import InterventionController
from utils.seed_questions import seed_questions_table
from utils.seed_interventions import seed_interventions_table
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def route_request(path, method, payload):
    dynamodb_client = DynamoDBClient()

    if path == '/questions/create' and method == 'POST':
        seed = payload.get("seed", False)

        if(seed):
            seed_questions_table()
            return 200, {'success': True, 'message': "Initial questions were successfully created in database."}

        questions_batch = payload.get('questions_batch', [])
        if not questions_batch:
            return 400, {'error': 'questions_batch is required'}
        
        question_controller = QuestionController(questions_batch, dynamodb_client)
        result = question_controller.batch_create()
        return 200, {'success': True, 'message': result}
    
    elif path == '/interventions/create' and method == 'POST':
        seed = payload.get("seed", False)

        if(seed):
            seed_interventions_table()
            return 200, {'success': True, 'message': "Initial intervention data was successfully created in database."}
        
        interventions_batch = payload.get('interventions_batch', [])
        if not interventions_batch:
            return 400, {'error': 'interventions_batch is required'}
        intervention_controller = InterventionController(interventions_batch, dynamodb_client)
        result = intervention_controller.batch_create()
        return 200, {'success': True, 'message': result}
    
    else:
        return 404, {'error': f'Route {method} {path} not found'}


def handler(event, context):
    try:
        path = event.get('rawPath', '') or event.get("path", "")
        method = event.get('httpMethod', 'POST')
        body = event.get('body', '{}')
        
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body
        
        status_code, response_body = route_request(path, method, payload)
        
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