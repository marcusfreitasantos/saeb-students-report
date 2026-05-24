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
            "region_name": "sa-east-1",
        }

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
    
    
    def list(self, table_name: str, limit: int, next_token: dict):
        try:
            table = self.dynamodb.Table(table_name)

            if(next_token):
                response = table.scan(Limit=limit, ExclusiveStartKey=next_token)
            else:
                response = table.scan(Limit=limit)

            return {"total": len(response["Items"]), "next_token": response.get("LastEvaluatedKey", None), "items": response['Items']}
        except ClientError as e:
            logger.error(
                f"Error occurred while fetching items from table: {e}.",
                exc_info=True,
                extra={"table_name": table_name}
            )
            raise