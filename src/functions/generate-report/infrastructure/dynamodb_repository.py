import boto3
import logging
import json
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
            table = self.dynamodb.Table(table_name)

            # measure item size to avoid DynamoDB item size limit (400 KB)
            try:
                item_json = json.dumps(new_item, default=str)
                item_size = len(item_json.encode("utf-8"))
                if item_size > 400000:
                    logger.error(f"Item exceeds DynamoDB size limit: {item_size} bytes")
                    raise ValueError("DynamoDB item size exceeds 400 KB limit")
            except Exception:
                logger.warning("Could not measure item size before saving")

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

    def list_by_descriptors(self, table_name: str, descriptors: list[str], projection: list[str] | None = None):
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
            # Build scan params; include ProjectionExpression when requested to reduce payload
            if projection:
                expr_names = {}
                proj_parts = []
                for i, attr in enumerate(projection):
                    key = f"#p{i}"
                    expr_names[key] = str(attr)
                    proj_parts.append(key)

                scan_params = {
                    "FilterExpression": filter_expression,
                    "ProjectionExpression": ", ".join(proj_parts),
                    "ExpressionAttributeNames": expr_names,
                }
            else:
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