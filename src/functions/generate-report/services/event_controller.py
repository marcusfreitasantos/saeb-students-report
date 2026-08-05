from application.event_usecase import EventUseCase
from application.report_usecase import ReportUseCase
import json
import re
from datetime import datetime
from infrastructure.config.settings import settings

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
            )
        
        # CASE HTTP GET EVENT
        if event.get("requestContext", {}).get("http", {}).get("method") == "GET":
            params = event.get("queryStringParameters") or {}
            filekey = params.get("filekey")

            if not filekey:
                raise ValueError("Missing required query parameter: filekey")
            
            events = EventUseCase(self.db_client, self.sqs_client)
            items = events.get_item(filekey)

            # For completed events, resolve download URLs on demand by listing S3
            try:
                key_without_bucket = filekey.split("/", 1)[1] if "/" in filekey else filekey
                safe_key = re.sub(r"[^a-zA-Z0-9/_-]+", "-", key_without_bucket).strip("-/")
                prefix = f"reports/{safe_key}/"
                bucket = settings.S3_OUTPUT_BUCKET_NAME

                s3_list = None
                try:
                    s3_list = self.s3_client.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
                except Exception:
                    s3_list = {"KeyCount": 0}

                available_keys = set()
                for content in s3_list.get("Contents", []) if s3_list.get("KeyCount", 0) else []:
                    available_keys.add(content.get("Key"))

                for item in items:
                    if str(item.get("status", "")).upper() == "COMPLETED":
                        # find pdf/docx keys under the prefix
                        pdf_key = next((k for k in available_keys if k.endswith("relatorio-saeb.pdf")), None)
                        docx_key = next((k for k in available_keys if k.endswith("relatorio-saeb.docx")), None)

                        download_urls = {}
                        if pdf_key:
                            download_urls["pdf"] = self.s3_client.download_url(bucket, pdf_key)
                        if docx_key:
                            download_urls["docx"] = self.s3_client.download_url(bucket, docx_key)

                        if download_urls:
                            item["downloadUrl"] = download_urls

            except Exception:
                # don't break status response if URL resolution fails
                pass

            return items

        else:
            raise ValueError("Unsupported event source")
