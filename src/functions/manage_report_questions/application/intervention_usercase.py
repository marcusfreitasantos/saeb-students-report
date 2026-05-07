import uuid
from domain.entities.intervention import Intervention
from domain.entities.intervention import InterventionData
from infrastructure.config.settings import settings

class CreateInterventionUseCase:

    interventions_table_name = settings.DYNAMMO_INTERVENTIONS_TABLE

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