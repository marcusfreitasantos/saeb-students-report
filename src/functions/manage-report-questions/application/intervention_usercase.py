import uuid
from domain.entities.intervention import Intervention
from domain.entities.intervention import InterventionData
from infrastructure.config.settings import settings
import json

class InterventionUseCase:

    interventions_table_name = settings.DYNAMO_INTERVENTIONS_TABLE

    def __init__(self, repository):
        self.repository = repository

    def build(self, descriptor: str, skill: str, category: str, intervention_data: list[InterventionData]):
                
        new_intervention = Intervention(
            id=str(uuid.uuid4()),
            descriptor=descriptor,
            skill=skill,
            category=category,
            intervention_data=intervention_data
        )

        self.repository.save(self.interventions_table_name, new_intervention.to_dict())
        return new_intervention
    
    def list(self, limit: int, next_token: str): 
        next_token_data = json.loads(next_token) if next_token else {}
        items_found = self.repository.list(self.interventions_table_name, limit, next_token_data)
        return items_found