import boto3
import logging
from botocore.exceptions import ClientError
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DynamoDBClient:
    def __init__(self):
        dynamodb_params = {
            "service_name": "dynamodb",
            "region_name": "us-east-1",
        }

        print(settings.DYNAMODB_ENDPOINT)
        logger.error(settings.DYNAMODB_ENDPOINT)

        if settings.DYNAMODB_ENDPOINT:
            dynamodb_params["endpoint_url"] = settings.DYNAMODB_ENDPOINT

        self.dynamodb = boto3.resource(**dynamodb_params)


    def save(self, table_name: str, new_item):
        try:
            table = self.dynamodb.Table(table_name)
        
            table.put_item(
                Item=new_item
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while inserting item into table: {e}.",
                exc_info=True,
                extra={"table_name": table_name, "item": new_item}
            )
            raise



    def delete(self, table_name: str, item_to_delete: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            table.delete_item(
                Key={'id': item_to_delete}
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while deleting item from table: {e}.",
                exc_info=True,
                extra={"table_name": table_name}
            )
            raise


    def get(self, table_name: str, item_key: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            return table.get_item(
                Key={'id': item_key}
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while fetching items from table: {e}.",
                exc_info=True,
                extra={"table_name": table_name}
            )
            raise
    
    def list(self, table_name: str):
        try:
            table = self.dynamodb.Table(table_name)

            response = table.scan()
            items = response['Items']

            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])

            return items
        except ClientError as e:
            logger.error(
                f"Error occurred while fetching items from table: {e}.",
                exc_info=True,
                extra={"table_name": table_name}
            )
            raise