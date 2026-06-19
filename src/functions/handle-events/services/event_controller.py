from application.event_usecase import EventUseCase
from datetime import datetime

class EventController:
    def __init__(self, event_data, db_client=None):
        self.event_data = event_data
        self.db_client = db_client


    def handle(self, event_data):
        event_usecase = EventUseCase(self.db_client)
        now = datetime.now()
        fileKey = f"{event_data['Records'][0]['s3']['bucket']['name']}/{event_data['Records'][0]['s3']['object']['key']}"

        result = event_usecase.build(
            fileKey,
            "STARTED",
            now.isoformat(),
            None,
        )

        return result

    
    def get_item(self, filekey: str):
        events = EventUseCase(self.db_client)       
        return events.get_item(filekey)
