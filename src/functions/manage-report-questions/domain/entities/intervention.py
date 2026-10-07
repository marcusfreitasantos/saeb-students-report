from dataclasses import dataclass
from dataclasses import dataclass, asdict


@dataclass
class InterventionData:
    type: str
    title: str
    challenge: str
    integration: str

    def __post_init__(self):
        if not self.type or not isinstance(self.type, str):
            raise ValueError("type cannot be empty and must be a string")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("title cannot be empty and must be a string")
        if not self.challenge or not isinstance(self.challenge, str):
            raise ValueError("challenge cannot be empty and must be a string")
        if not self.integration or not isinstance(self.integration, str):
            raise ValueError("integration cannot be empty and must be a string")


@dataclass
class Intervention:
    id: str
    descriptor: str
    skill: str
    category: str
    intervention_data: list[InterventionData]

    def __post_init__(self):
        if not self.descriptor or not isinstance(self.descriptor, str):
            raise ValueError("descriptor cannot be empty and must be a string")
        if not self.skill or not isinstance(self.skill, str):
            raise ValueError("skill cannot be empty and must be a string")
        if not self.category or not isinstance(self.category, str):
            raise ValueError("category cannot be empty and must be a string")
        if not isinstance(self.intervention_data, list) or not all(isinstance(i, InterventionData) for i in self.intervention_data):
            raise ValueError("interventions must be a list of InterventionData objects")

    def to_dict(self):
        item = asdict(self)
        return item