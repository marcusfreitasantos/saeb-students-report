import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
    DYNAMO_QUESTIONS_TABLE= os.getenv("DYNAMO_QUESTIONS_TABLE")
    DYNAMO_INTERVENTIONS_TABLE= os.getenv("DYNAMO_INTERVENTIONS_TABLE")

settings = Settings()