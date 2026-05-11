import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
    DYNAMO_QUESTIONS_TABLE= os.getenv("DYNAMO_QUESTIONS_TABLE")
    DYNAMMO_INTERVENTIONS_TABLE= os.getenv("DYNAMMO_INTERVENTIONS_TABLE")

settings = Settings()