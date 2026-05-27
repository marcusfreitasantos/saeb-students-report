import json
import logging
from services.bucket_controller import BucketController
from infrastructure.bucket_repository import S3Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        s3_client = S3Client()
        
        bucket_controller = BucketController(s3_client=s3_client)

        # generate signedUrl to upload file to s3
        response = bucket_controller.get_signed_url()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response)
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