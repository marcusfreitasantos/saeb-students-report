import os

class Settings:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://host.docker.internal:8000")

settings = Settings()