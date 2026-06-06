from application.event_usecase import EventUseCase
from datetime import datetime


class EventController:
    def __init__(self, event_data, db_client=None):
        self.event_data = event_data
        self.db_client = db_client


    def handle(self, event_data):
        create_event = EventUseCase(self.db_client)
        now = datetime.now()
        fileKey = f"{event_data['Records'][0]['s3']['bucket']['name']}/{event_data['Records'][0]['s3']['object']['key']}"

        return create_event.build(
            fileKey,
            "STARTED",
            now.isoformat(),
            None,
        )

    
    def list(self, params):
        events = EventUseCase(self.db_client)
        
        try:
            limit = int((params or {}).get("limit", 10))
            next_token = (params or {}).get("next_token", "")

        except (TypeError, ValueError):
            limit = 10
            next_token = ""

        return events.list(limit, next_token)

