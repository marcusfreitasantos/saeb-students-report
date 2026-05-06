from dataclasses import dataclass
from typing import List

@dataclass
class InterventionData:
    index: int
    type: str
    title: str
    challenge: str
    integration: str

    def __post_init__(self):
        if not isinstance(self.index, int) or self.index <= 0:
            raise ValueError("index must be a positive integer")
        if not self.type or not isinstance(self.type, str):
            raise ValueError("type cannot be empty and must be a string")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("title cannot be empty and must be a string")
        if not self.challenge or not isinstance(self.challenge, str):
            raise ValueError("challenge cannot be empty and must be a string")
        if not self.integration or not isinstance(self.integration, str):
            raise ValueError("integration cannot be empty and must be a string")

@dataclass
class Descriptor:
    index: int
    skill: str
    interventions: List[InterventionData]

    def __post_init__(self):
        if not isinstance(self.index, int) or self.index <= 0:
            raise ValueError("index must be a positive integer")
        if not self.skill or not isinstance(self.skill, str):
            raise ValueError("skill cannot be empty and must be a string")
        if not isinstance(self.interventions, list) or not all(isinstance(i, InterventionData) for i in self.interventions):
            raise ValueError("interventions must be a list of InterventionData objects")


@dataclass
class Intervention:
    category: str
    descriptors: List[Descriptor]