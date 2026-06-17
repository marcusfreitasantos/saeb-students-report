import logging
import re
import uuid
from datetime import datetime

from application.report_builder import ReportBuilder
from application.report_builder import SpreadsheetReportProcessor
from domain.entities.report import ReportResult
from infrastructure.config.settings import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReportUseCase:

    questions_table_name = settings.DYNAMO_QUESTIONS_TABLE
    interventions_table_name = settings.DYNAMO_INTERVENTIONS_TABLE
    output_bucket_name = settings.S3_OUTPUT_BUCKET_NAME
    static_bucket_name = settings.S3_STATIC_BUCKET_NAME

    def __init__(self, repository, storage):
        self.repository = repository
        self.storage = storage
        self.processor = SpreadsheetReportProcessor()
        self.report_builder = ReportBuilder()
    
    def build(self, filekey: str) -> ReportResult:
        # STEP 1 - GET FILE FROM BUCKET
        # STEP 2 - READ AND VALIDATE FILE
        # STEP 3 - PROCESS DATA AND GENERATE STUDENTS REPORT 
        # STEP 4 - SEND DATA TO GENERATE GRAPHS
        # STEP 5 - GET QUESTIONS FROM DATABASE
        # STEP 6 - GET INTERVENTIONS FROM DATABASE
        # STEP 7 - STRUCTURE ALL DATA INTO HTML/DOCX/PDF
        # STEP 8 - SAVE FILE IN BUCKET AND GET DOWNLOAD URL
        try:
            spreadsheet_data = self.storage.get_file(filekey)
            diagnosis = self.processor.process(spreadsheet_data)
            descriptors = diagnosis.critical_descriptors
            questions = self._group_by_descriptor(
                self.repository.list_by_descriptors(
                    self.questions_table_name,
                    descriptors,
                )
            )
            interventions = self._group_by_descriptor(
                self.repository.list_by_descriptors(
                    self.interventions_table_name,
                    descriptors,
                )
            )
            artifacts = self.report_builder.build(diagnosis, questions, interventions)
            base_key = self._report_base_key(filekey)

            docx_key = f"{base_key}/relatorio-saeb.docx"
            pdf_key = f"{base_key}/relatorio-saeb.pdf"
            html_key = f"{base_key}/index.html"

            self.storage.put_file(
                self.output_bucket_name,
                docx_key,
                artifacts.docx,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            self.storage.put_file(
                self.output_bucket_name,
                pdf_key,
                artifacts.pdf,
                "application/pdf",
            )
            self.storage.put_file(
                self.static_bucket_name,
                html_key,
                artifacts.html,
                "text/html; charset=utf-8",
            )

            return ReportResult(
                success=True,
                message="Relatorio gerado com sucesso.",
                pdf_download_url=self.storage.download_url(self.output_bucket_name, pdf_key),
                docx_download_url=self.storage.download_url(self.output_bucket_name, docx_key),
                html_url=self.storage.object_url(self.static_bucket_name, html_key),
            )

        
        except ClientError as e:
            logger.error(
                f"Error occurred while generating report event: {e}.",
                exc_info=True,
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
