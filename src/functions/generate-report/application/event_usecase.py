import uuid
from domain.entities.event import Event
from domain.entities.event import StatusType
from infrastructure.config.settings import settings
import json
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class EventUseCase:

    reports_table_name = settings.DYNAMO_REPORTS_TABLE
    operation_name = "GenerateReportEvent"

    def __init__(self, repository):
        self.repository = repository


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
        downloadUrl: str | None,
        error: ClientError,
    ) -> Event:
        error_event = Event(
            id=str(uuid.uuid4()),
            filekey=filekey,
            status=StatusType.CANCELLED,
            downloadUrl=downloadUrl,
            createdAt=createdAt,
            error=str(error),
        )

        self.repository.save(self.reports_table_name, error_event.to_dict())
        return error_event
    

    def build(self, filekey: str, status: str, createdAt: str, downloadUrl: str = None) -> Event:
        try:
            try:
                new_event = Event(
                    id=str(uuid.uuid4()),
                    filekey=filekey,
                    status=self.status_map(status),
                    downloadUrl=downloadUrl,
                    createdAt=createdAt,
                )

                self.repository.save(self.reports_table_name, new_event.to_dict())
                return new_event
            except Exception as e:
                raise self.to_client_error(e) from e
        
        except ClientError as e:
            logger.error(
                f"Error occurred while generating report event: {e}.",
                exc_info=True,
            )

            self.save_error_event(filekey, createdAt, downloadUrl, e)
            raise


    def list(self, limit: int, next_token: str): 
        next_token_data = json.loads(next_token) if next_token else {}
        items_found = self.repository.list(self.reports_table_name, limit, next_token_data)
        return items_found
