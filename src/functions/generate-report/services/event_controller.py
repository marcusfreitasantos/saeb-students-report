from application.event_usecase import EventUseCase
from application.report_usecase import ReportUseCase
import json
from datetime import datetime

class EventController:
    def __init__(self, event, db_client=None, s3_client=None, sqs_client=None):
        self.event = event
        self.db_client = db_client
        self.s3_client = s3_client
        self.sqs_client = sqs_client


    def handle(self, event):
        records = event.get("Records", [])
        
        # CASE SQS EVENT
        if bool(records and records[0].get("eventSource") == "aws:sqs"):
            body = records[0].get("body")
            if not body:
                raise ValueError("SQS record has no body")

            if isinstance(body, str):
                try:
                    body_json = json.loads(body)
                except Exception:
                    raise ValueError("SQS body is not valid JSON")
            else:
                body_json = body

            key = body_json.get("key")
            if not key:
                raise ValueError("SQS message body must contain 'key'")
            
            report_usecase = ReportUseCase(self.db_client, self.s3_client, self.sqs_client)
            return report_usecase.build(key)
        
        # CASE S3 EVENT
        if bool(records and records[0].get("eventSource") == "aws:s3"):
            event_usecase = EventUseCase(self.db_client, self.sqs_client)
            now = datetime.now()
            fileKey = f"{self.event['Records'][0]['s3']['object']['key']}"

            return event_usecase.build(
                fileKey,
                "STARTED",
                now.isoformat(),
                None,
            )
        
        # CASE HTTP GET EVENT
        if event.get("requestContext", {}).get("http", {}).get("method") == "GET":
            params = event.get("queryStringParameters") or {}
            filekey = params.get("filekey")

            if not filekey:
                raise ValueError("Missing required query parameter: filekey")
            
            events = EventUseCase(self.db_client, self.sqs_client)
            return events.get_item(filekey)

        else:
            raise ValueError("Unsupported event source")
