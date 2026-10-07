from application.intervention_usercase import InterventionUseCase
from domain.entities.intervention import InterventionData

class InterventionController:
    def __init__(self, interventions_batch, db_client=None):
        self.interventions_batch = interventions_batch
        self.db_client = db_client


    def create(self, intervention_data):
        create_intervention = InterventionUseCase(self.db_client)

        intervention_details = [
            InterventionData(**item)
            for item in intervention_data["intervention_data"]
        ]

        return create_intervention.build(
            intervention_data["descriptor"],
            intervention_data["skill"],
            intervention_data["category"],
            intervention_details,
        )
    
    def batch_create(self):
        for batch in self.interventions_batch:
            self.create(batch)
        return f'All {str(len(self.interventions_batch))} interventions sucessfully created.'
    
    def list(self, params):
        interventions = InterventionUseCase(self.db_client)
        
        try:
            limit = int((params or {}).get("limit", 10))
            next_token = (params or {}).get("next_token", "")


        except (TypeError, ValueError):
            limit = 10
            next_token = ""

        return interventions.list(limit, next_token)

