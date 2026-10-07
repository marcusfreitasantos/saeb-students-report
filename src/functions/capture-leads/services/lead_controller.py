from application.lead_usecase import LeadUseCase, ValidationError


class LeadController:
    def __init__(self, dynamodb_client):
        self.lead_usecase = LeadUseCase(dynamodb_client=dynamodb_client)

    def create(self, payload: dict):
        try:
            lead = self.lead_usecase.create(payload)
            return 201, {"data": lead}
        except ValidationError as e:
            return 400, {"error": str(e)}
