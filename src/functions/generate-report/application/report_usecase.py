import logging
import re
import uuid
from datetime import datetime
from .report_builder import ReportBuilder
from .sheet_processor_usecase import SpreadsheetReportProcessor
from domain.entities.report import ReportResult
from infrastructure.config.settings import settings
from botocore.exceptions import ClientError
from .event_usecase import EventUseCase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReportUseCase:

    questions_table_name = settings.DYNAMO_QUESTIONS_TABLE
    interventions_table_name = settings.DYNAMO_INTERVENTIONS_TABLE
    output_bucket_name = settings.S3_OUTPUT_BUCKET_NAME
    input_bucket_name = settings.S3_INPUT_BUCKET_NAME

    def __init__(self, repository, storage):
        self.repository = repository
        self.storage = storage
        self.processor = SpreadsheetReportProcessor()
        self.report_builder = ReportBuilder()
    
    def build(self, filekey: str) -> ReportResult:
        try:
            spreadsheet_data = self.storage.get_file(self.input_bucket_name, filekey)
            # diagnosis = self.processor.process(spreadsheet_data)
            # descriptors = diagnosis.critical_descriptors
            # questions = self._group_by_descriptor(
            #     self.repository.list_by_descriptors(
            #         self.questions_table_name,
            #         descriptors,
            #     )
            # )
            # interventions = self._group_by_descriptor(
            #     self.repository.list_by_descriptors(
            #         self.interventions_table_name,
            #         descriptors,
            #     )
            # )
            # artifacts = self.report_builder.build(diagnosis, questions, interventions)
            # base_key = self._report_base_key(filekey)

            # docx_key = f"{base_key}/relatorio-saeb.docx"
            # pdf_key = f"{base_key}/relatorio-saeb.pdf"

            # self.storage.put_file(
            #     self.output_bucket_name,
            #     docx_key,
            #     artifacts.docx,
            #     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            # )
            # self.storage.put_file(
            #     self.output_bucket_name,
            #     pdf_key,
            #     artifacts.pdf,
            #     "application/pdf",
            # )

            event_usecase = EventUseCase(self.repository)
            event_usecase.build(
                filekey,
                "COMPLETED",
                datetime.now().isoformat(),
                "https://example.com/download/report.pdf",
            )

            return ReportResult(
                success=True,
                message="Relatorio gerado com sucesso.",
                #pdf_download_url=self.storage.download_url(self.output_bucket_name, pdf_key),
                #docx_download_url=self.storage.download_url(self.output_bucket_name, docx_key),
            )

        
        except ClientError as e:
            logger.error(
                f"Error occurred while generating report event: {e}.",
                exc_info=True,
            )

            event_usecase = EventUseCase(self.repository)
            event_usecase.save_error_event(
                filekey=filekey,
                createdAt=datetime.now().isoformat(),
                downloadUrl=None,
                error=e,
            )

            return ReportResult(
                success=False,
                message=f"Erro ao gerar relatorio: {e}",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while generating report: {e}.",
                exc_info=True,
            )

            return ReportResult(
                success=False,
                message=f"Erro ao gerar relatorio: {e}",
            )

    def _group_by_descriptor(self, items: list[dict]) -> dict[str, list[dict]]:
        grouped_items: dict[str, list[dict]] = {}

        for item in items:
            descriptor = str(item.get("descriptor", "")).upper()
            if not descriptor:
                continue

            grouped_items.setdefault(descriptor, []).append(item)

        return grouped_items

    def _report_base_key(self, filekey: str) -> str:
        key_without_bucket = filekey.split("/", 1)[1] if "/" in filekey else filekey
        safe_key = re.sub(r"[^a-zA-Z0-9/_-]+", "-", key_without_bucket).strip("-/")
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"reports/{safe_key}/{now}-{uuid.uuid4()}"
