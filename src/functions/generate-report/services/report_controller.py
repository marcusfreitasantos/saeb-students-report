from application.report_usecase import ReportUseCase
from datetime import datetime
from infrastructure.s3_repository import S3Client


class ReportController:
    def __init__(self, event_data, db_client=None):
        self.event_data = event_data
        self.db_client = db_client


    def handle(self, event_data):
        report_usecase = ReportUseCase(self.db_client, S3Client())
        fileKey = f"{event_data['Records'][0]['s3']['bucket']['name']}/{event_data['Records'][0]['s3']['object']['key']}"

        result = report_usecase.build(fileKey)
        finished_at = datetime.now().isoformat()

        event_usecase.build(
            fileKey,
            "COMPLETED" if result.success else "CANCELLED",
            finished_at,
            result.pdf_download_url,
        )

        return result

    
    def get_item(self, filekey: str):
        events = EventUseCase(self.db_client)       
        return events.get_item(filekey)
