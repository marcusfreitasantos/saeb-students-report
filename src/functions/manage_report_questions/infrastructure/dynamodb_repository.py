import boto3
import logging
from botocore.exceptions import ClientError
from infrastructure.config.settings import settings
from domain.entities.question import Question

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name="us-east-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT
        )


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



    def delete(self, table_name: str, item_to_delete: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            table.delete_item(
                Key={'id': item_to_delete}
            )
        except ClientError as e:
            logger.error(
                "Error occurred while deleting item from table.",
                exc_info=True,
                extra={"table_name": table_name, "item_key": item_to_delete}
            )


    def get(self, table_name: str, item_key: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            return table.get_item(
                Key={'id': item_key}
            )
        except ClientError as e:
            logger.error(
                "Error occurred while fetching item from table.",
                exc_info=True,
                extra={"table_name": table_name, "item_key": item_key}
            )
            return None