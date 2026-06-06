import uuid
from domain.entities.event import Event
from domain.entities.event import StatusType
from infrastructure.config.settings import settings
import json

class EventUseCase:

    reports_table_name = settings.DYNAMO_REPORTS_TABLE

    def __init__(self, repository):
        self.repository = repository


    def status_map(self, status: str):
        if(status == "STARTED"): return StatusType.STARTED
        if(status == "IN_PROGRESS"): return StatusType.IN_PROGRESS
        if(status == "COMPLETED"): return StatusType.COMPLETED
        if(status == "CANCELLED"): return StatusType.CANCELLED
        return None
    

    def build(self, filekey: str, status: str, downloadUrl: str, expirationDate: str, createdAt: str, error: str = None) -> Event:
        new_event = Event(
            id=str(uuid.uuid4()),
            filekey=filekey,
            status=self.status_map(status),
            downloadUrl=downloadUrl,
            expirationDate=expirationDate,
            createdAt=createdAt,
            error=error
        )

        self.repository.save(self.reports_table_name, new_event.to_dict())
        return new_event

    def list(self, limit: int, next_token: str): 
        next_token_data = json.loads(next_token) if next_token else {}
        items_found = self.repository.list(self.reports_table_name, limit, next_token_data)
        return items_found