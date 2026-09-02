import logging
import random
import re
import uuid
import time
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

    def __init__(self, db_repository, s3_repository, sqs_repository):
        self.db_repository = db_repository
        self.s3_repository = s3_repository
        self.sqs_repository = sqs_repository
        self.processor = SpreadsheetReportProcessor()
        self.report_builder = ReportBuilder()
    
    def build(self, filekey: str) -> ReportResult:
        try:
            start_total = time.time()

            t0 = time.time()
            spreadsheet_data = self.s3_repository.get_file(self.input_bucket_name, filekey)
            t1 = time.time()
            logger.info(f"S3 download took {t1 - t0:.2f}s for {filekey}")

            t0 = time.time()
            diagnosis = self.processor.process(spreadsheet_data)
            t1 = time.time()
            logger.info(f"Spreadsheet processing took {t1 - t0:.2f}s for {filekey}")

            descriptors = diagnosis.critical_descriptors

            # request only needed attributes to reduce scan payload
            question_projection = ["descriptor", "description", "options"]
            intervention_projection = ["descriptor", "skill", "intervention_data"]

            t0 = time.time()
            questions_items = self.db_repository.list_by_descriptors(
                self.questions_table_name,
                descriptors,
                projection=question_projection,
            )
            questions = self._group_by_descriptor(self._randomize_and_limit(questions_items, limit=10))
            t1 = time.time()
            logger.info(f"Questions lookup took {t1 - t0:.2f}s")

            t0 = time.time()
            interventions_items = self.db_repository.list_by_descriptors(
                self.interventions_table_name,
                descriptors,
                projection=intervention_projection,
            )
            interventions = self._group_by_descriptor(self._randomize_and_limit(interventions_items, limit=10))
            t1 = time.time()
            logger.info(f"Interventions lookup took {t1 - t0:.2f}s")

            t0 = time.time()
            artifacts = self.report_builder.build(diagnosis, questions, interventions)
            t1 = time.time()
            logger.info(f"Report artifacts build took {t1 - t0:.2f}s")
            base_key = self._report_base_key(filekey)

            pdf_key = f"{base_key}/relatorio-saeb.pdf"

            self.s3_repository.put_file(
                self.output_bucket_name,
                pdf_key,
                artifacts.pdf,
                "application/pdf",
            )

            logger.info(f"S3 upload completed for {pdf_key}")

            event_usecase = EventUseCase(self.db_repository, self.sqs_repository)
            event_usecase.build(
                filekey,
                "COMPLETED",
                datetime.now().isoformat(),
            )

            total_elapsed = time.time() - start_total
            logger.info(f"Total report build time for {filekey}: {total_elapsed:.2f}s")

            return ReportResult(
                success=True,
                message="Relatorio gerado com sucesso.",
            )

        
        except ClientError as e:
            logger.error(
                f"Error occurred while generating report event: {e}.",
                exc_info=True,
            )

            event_usecase = EventUseCase(self.db_repository, self.sqs_repository)
            event_usecase.save_error_event(
                filekey=filekey,
                createdAt=datetime.now().isoformat(),
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

            try:
                event_usecase = EventUseCase(self.db_repository, self.sqs_repository)
                client_error = event_usecase.to_client_error(e)
                event_usecase.save_error_event(
                    filekey=filekey,
                    createdAt=datetime.now().isoformat(),
                    error=client_error,
                )
            except Exception:
                logger.exception("Failed to persist error event for unexpected exception.")

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

        for descriptor, descriptor_items in grouped_items.items():
            random.shuffle(descriptor_items)
            grouped_items[descriptor] = descriptor_items[:10]

        return grouped_items

    def _randomize_and_limit(self, items: list[dict], limit: int = 10) -> list[dict]:
        if len(items) <= limit:
            random.shuffle(items)
            return items

        return random.sample(items, k=limit)

    def _report_base_key(self, filekey: str) -> str:
        key_without_bucket = filekey.split("/", 1)[1] if "/" in filekey else filekey
        safe_key = re.sub(r"[^a-zA-Z0-9/_-]+", "-", key_without_bucket).strip("-/")
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"reports/{safe_key}/{now}-{uuid.uuid4()}"
