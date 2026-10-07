import json
import logging

import boto3
from botocore.exceptions import ClientError

from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DynamoDBClient:
    def __init__(self):
        dynamodb_params = {
            "service_name": "dynamodb",
            "region_name": settings.AWS_REGION,
        }

        if settings.DYNAMODB_ENDPOINT:
            dynamodb_params["endpoint_url"] = settings.DYNAMODB_ENDPOINT

        self.dynamodb = boto3.resource(**dynamodb_params)

    def save(self, table_name: str, new_item: dict):
        try:
            item_size = len(json.dumps(new_item, default=str).encode("utf-8"))
            if item_size > 400000:
                raise ValueError("DynamoDB item size exceeds 400 KB limit")

            table = self.dynamodb.Table(table_name)
            table.put_item(
                Item=new_item,
                ConditionExpression="attribute_not_exists(id)",
            )
        except ClientError as e:
            logger.error(
                f"Error occurred while inserting lead into table: {e}.",
                exc_info=True,
                extra={"table_name": table_name, "item": new_item},
            )
            raise
