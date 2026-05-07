import json
from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController
from infrastructure.config.settings import settings



def process_questions_batch(questions_batch):

    tables_to_create = [
        {
            "table_name": settings.DYNAMO_QUESTIONS_TABLE
        },
        {
            "table_name": settings.DYNAMMO_INTERVENTIONS_TABLE
        }
    ]

    dynamodb_client = DynamoDBClient()
    dynamodb_client.db_setup(tables_to_create)
    
    question_controller = QuestionController(questions_batch, dynamodb_client)
    result = question_controller.batch_create()
    
    return result


def handler(event, context):
    try:
        body = event.get('body', '{}')
        
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body
        
        questions_batch = payload.get('questions_batch', [])
        
        if not questions_batch:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'questions_batch is required'})
            }
        
        result = process_questions_batch(questions_batch)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': True, 'message': result})
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