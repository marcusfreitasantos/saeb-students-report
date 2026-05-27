import uuid
from datetime import date, datetime

class BucketUseCase:
    def __init__(self, repository):
        self.repository = repository

    def get_signed_url(self):
        now = datetime.now()
        day = date.today().day
        month = now.month
        year = date.today().year

        key = f"input-files/{year}/{month}/{day}/{uuid.uuid4()}/students-data.xlsx"
        signed_url = self.repository.presigned_url(key)
        return signed_url
    
