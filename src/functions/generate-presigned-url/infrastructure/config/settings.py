import os

class Settings:
    S3_INPUT_BUCKET_NAME = os.getenv("S3_INPUT_BUCKET_NAME")
    BUCKET_ENDPOINT= os.getenv("BUCKET_ENDPOINT")

settings = Settings()