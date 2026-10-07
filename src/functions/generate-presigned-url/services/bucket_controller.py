from application.bucket_usecase import BucketUseCase

class BucketController:
    def __init__(self, s3_client=None):
        self.s3_client = s3_client
        
    def get_signed_url(self):
        bucket_use_case = BucketUseCase(self.s3_client)
        signed_url = bucket_use_case.get_signed_url()
        return signed_url
        
