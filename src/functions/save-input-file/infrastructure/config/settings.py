import os

class Settings:
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    BUCKET_ENDPOINT= os.getenv("BUCKET_ENDPOINT")

settings = Settings()