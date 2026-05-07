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
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT
        )

    def create_new_table(self, table_name: str):
        self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )


    def check_table_exists(self, table_name: str):
        try:
            table = self.dynamodb.Table(table_name)
            logger.debug(table.table_status)
            return True
        except ClientError:
            logger.info("Table does not exist. Creating...", extra={"table_name": table_name})
            return False


    def db_setup(self, tables_to_create):
        for table in tables_to_create:
            if not self.check_table_exists(table["table_name"]):
                self.create_new_table(table["table_name"])
                logger.info("Successfully created table.", extra={"table_name": table["table_name"]})


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