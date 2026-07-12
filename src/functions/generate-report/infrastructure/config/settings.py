import os
from urllib.parse import urlparse, urlunparse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

LOCALSTACK_LOCAL_HOSTS = {"localhost", "127.0.0.1", "localhost.localstack.cloud"}
SAM_LOCALSTACK_HOST = "host.docker.internal"


def normalize_localstack_endpoint(endpoint: str | None) -> str | None:
    if not endpoint:
        return None

    parsed_endpoint = urlparse(endpoint)

    if (
        os.getenv("AWS_SAM_LOCAL")
        and parsed_endpoint.hostname in LOCALSTACK_LOCAL_HOSTS
    ):
        netloc = SAM_LOCALSTACK_HOST

        if parsed_endpoint.port:
            netloc = f"{netloc}:{parsed_endpoint.port}"

        return urlunparse(parsed_endpoint._replace(netloc=netloc))

    return endpoint


class Settings:
    AWS_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "sa-east-1"
    DYNAMODB_ENDPOINT = normalize_localstack_endpoint(os.getenv("DYNAMODB_ENDPOINT"))
    BUCKET_ENDPOINT = normalize_localstack_endpoint(os.getenv("BUCKET_ENDPOINT"))
    SQS_ENDPOINT = normalize_localstack_endpoint(os.getenv("SQS_ENDPOINT"))
    SQS_QUEUE_URL = normalize_localstack_endpoint(os.getenv("SQS_QUEUE_URL"))
    SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")
    DYNAMO_QUESTIONS_TABLE= os.getenv("DYNAMO_QUESTIONS_TABLE")
    DYNAMO_INTERVENTIONS_TABLE= os.getenv("DYNAMO_INTERVENTIONS_TABLE")
    DYNAMO_REPORTS_TABLE= os.getenv("DYNAMO_REPORTS_TABLE")
    S3_INPUT_BUCKET_NAME= os.getenv("S3_INPUT_BUCKET_NAME")
    S3_OUTPUT_BUCKET_NAME= os.getenv("S3_OUTPUT_BUCKET_NAME")
    S3_STATIC_BUCKET_NAME= os.getenv("S3_STATIC_BUCKET_NAME")

settings = Settings()
