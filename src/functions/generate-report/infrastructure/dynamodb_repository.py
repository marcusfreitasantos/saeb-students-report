import boto3
import logging
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DynamoDBClient:
    filekey_index_name = "GetByFilekey"

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
            logger.info(f"Saving item to DynamoDB table: {table_name}, Enrpoint: {settings.DYNAMODB_ENDPOINT}")
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


    def get(self, table_name: str, filekey: str):
        try:
            table = self.dynamodb.Table(table_name)

            logger.info(
                f"Getting most recent item from DynamoDB table: {table_name}, filekey: {filekey}, gsi: {self.filekey_index_name}"
            )

            response = table.query(
                IndexName=self.filekey_index_name,
                KeyConditionExpression=Key("filekey").eq(filekey),
                ScanIndexForward=False,
                Limit=10,
            )
            return response.get("Items", [])
        
        except ClientError as e:
            logger.error(
                f"Error occurred while getting item from table: {e}.",
                exc_info=True,
                extra={
                    "table_name": table_name,
                    "filekey": filekey,
                    "gsi_name": self.filekey_index_name,
                }
            )
            raise

    def list_by_descriptors(self, table_name: str, descriptors: list[str]):
        try:
            if not descriptors:
                return []

            table = self.dynamodb.Table(table_name)
            descriptor_values = {str(descriptor).upper() for descriptor in descriptors}
            filter_expression = None

            for descriptor in descriptor_values:
                expression = Attr("descriptor").eq(descriptor)
                filter_expression = (
                    expression
                    if filter_expression is None
                    else filter_expression | expression
                )

            items = []
            scan_params = {"FilterExpression": filter_expression}

            while True:
                response = table.scan(**scan_params)
                items.extend(response.get("Items", []))

                last_key = response.get("LastEvaluatedKey")
                if not last_key:
                    break

                scan_params["ExclusiveStartKey"] = last_key

            return items
        
        except ClientError as e:
            logger.error(
                f"Error occurred while listing items from table: {e}.",
                exc_info=True,
                extra={
                    "table_name": table_name,
                    "descriptors": descriptors,
                }
            )
            raise