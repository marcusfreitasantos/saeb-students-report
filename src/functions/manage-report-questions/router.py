from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController
from services.intervention_controller import InterventionController
from utils.seed_questions import seed_questions_table
from utils.seed_interventions import seed_interventions_table
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def route_request(path, method, payload, params):
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
    
    elif path == '/questions/all' and method == 'GET':        
        question_controller = QuestionController([], dynamodb_client)
        result = question_controller.list(params)
        return 200, result
    
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
    
    elif path == '/interventions/all' and method == 'GET':        
        intervention_controller = InterventionController([], dynamodb_client)
        result = intervention_controller.list(params)
        return 200, result
    
    else:
        return 404, {'error': f'Route {method} {path} not found'}