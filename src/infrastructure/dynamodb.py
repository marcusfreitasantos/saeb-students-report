import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        region_name='dummy',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )

def create_new_table(table_name, sort_key):
    dynamodb.create_table(
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


def check_table_exists(table_name):
    try:
        table = dynamodb.Table(table_name)
        print(table.table_status)
        return True
    except ClientError:
        print("Table does not exist. Creating...")
        return False


def db_setup():
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
        if not check_table_exists(table["table_name"]):
            create_new_table(table["table_name"], table["sort_key"])
            print(f"Successfully created table '{table["table_name"]}'.")