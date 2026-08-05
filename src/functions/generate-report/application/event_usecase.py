import uuid
import json
from domain.entities.event import Event
from domain.entities.event import StatusType
from infrastructure.config.settings import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class EventUseCase:

    reports_table_name = settings.DYNAMO_REPORTS_TABLE
    sqs_queue_url = settings.SQS_QUEUE_URL
    sqs_queue_name = settings.SQS_QUEUE_NAME
    operation_name = "GenerateReportEvent"

    def __init__(self, db_repository, sqs_repository):
        self.db_repository = db_repository
        self.sqs_repository = sqs_repository


    def status_map(self, status: str):
        if(status == "STARTED"): return StatusType.STARTED
        if(status == "IN_PROGRESS"): return StatusType.IN_PROGRESS
        if(status == "COMPLETED"): return StatusType.COMPLETED
        if(status == "CANCELLED"): return StatusType.CANCELLED
        return None
    
    def to_client_error(self, error: Exception) -> ClientError:
        if isinstance(error, ClientError):
            return error

        return ClientError(
            {
                "Error": {
                    "Code": error.__class__.__name__,
                    "Message": str(error),
                }
            },
            self.operation_name,
        )

    def save_error_event(
        self,
        filekey: str,
        createdAt: str,
        error: ClientError,
    ) -> Event:
        error_event = Event(
            id=str(uuid.uuid4()),
            filekey=filekey,
            status=StatusType.CANCELLED,
            createdAt=createdAt,
            error=str(error),
        )

        try:
            self.db_repository.save(self.reports_table_name, error_event.to_dict())

        except Exception as e:
            logger.error(
                f"Failed to save error event for filekey {filekey}: {e}",
                exc_info=True,
            )
        return error_event
    

    def build(self, filekey: str, status: str, createdAt: str) -> Event:
        try:
            try:
                new_event = Event(
                    id=str(uuid.uuid4()),
                    filekey=filekey,
                    status=self.status_map(status),
                    createdAt=createdAt,
                )

                self.db_repository.save(self.reports_table_name, new_event.to_dict())

                # send SQS message
                if status == "STARTED":
                    sqs_msg_body = json.dumps({"key": new_event.to_dict()["filekey"]})
                    self.sqs_repository.send_message(self.sqs_queue_url, sqs_msg_body)

                return new_event
            except Exception as e:
                raise self.to_client_error(e) from e
        
        except ClientError as e:
            logger.error(
                f"Error occurred while generating report event: {e}.",
                exc_info=True,
            )

            self.save_error_event(filekey, createdAt, e)
            raise


    def get_item(self, filekey: str): 
        return self.db_repository.get(self.reports_table_name, filekey)
