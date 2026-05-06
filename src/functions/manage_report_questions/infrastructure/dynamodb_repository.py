import boto3
from botocore.exceptions import ClientError
from infrastructure.config.settings import settings
from domain.entities.question import Question


class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.DYNAMODB_ENDPOINT
        )

    def create_new_table(self, table_name: str, sort_key: str):
        self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': sort_key, 'KeyType': 'RANGE'} # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': sort_key, 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )


    def check_table_exists(self, table_name: str):
        try:
            table = self.dynamodb.Table(table_name)
            print(table.table_status)
            return True
        except ClientError:
            print("Table does not exist. Creating...")
            return False


    def db_setup(self):
        tables_to_create = [
            {
                "table_name": "saeb_questions",
                "sort_key": "descriptor"
            },
            {
                "table_name": "saeb_interventions",
                "sort_key": "category"
            }
        ]
    
        for table in tables_to_create:
            if not self.check_table_exists(table["table_name"]):
                self.create_new_table(table["table_name"], table["sort_key"])
                print(f"Successfully created table '{table["table_name"]}'.")


    def save(self, table_name: str, new_item: Question):
        try:
            table = self.dynamodb.Table(table_name)
        
            table.put_item(
                Item={
                    "id": new_item.id,
                    "descriptor": new_item.descriptor,
                    "level": new_item.level.value,
                    "description": new_item.description,
                    "options": new_item.options,
                    "answer": new_item.answer,
                }
            )
        except ClientError as e:
            print(f"Error occurred while inserting item into table '{table_name}': {e}")



    def delete(self, table_name: str, item_to_delete: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            table.delete_item(
                Key={'id': item_to_delete}
            )
        except ClientError as e:
            print(f"Error occurred while deleting item from table '{table_name}': {e}")


    def get(self, table_name: str, item_key: str):
        try:
            table = self.dynamodb.Table(table_name)
        
            return table.get_item(
                Key={'id': item_key}
            )
        except ClientError as e:
            print(f"Error occurred while fetching item from table '{table_name}': {e}")
            return None