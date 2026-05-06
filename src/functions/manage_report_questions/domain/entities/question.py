
from enum import Enum
from dataclasses import dataclass
from typing import List

class DifficultyLevel(Enum):
    EASY = "Fácil"
    MEDIUM = "Médio"
    HARD = "Difícil"

@dataclass
class Question:
    id: str
    descriptor: str
    level: DifficultyLevel
    description: str
    options: List[str]
    answer: str

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("id cannot be empty and must be a string")
        if not self.descriptor or not isinstance(self.descriptor, str):
            raise ValueError("descriptor cannot be empty and must be a string")
        if not self.level or not isinstance(self.level, DifficultyLevel):
            raise ValueError("level cannot be empty and must be a DifficultyLevel type")
        if not self.description or not isinstance(self.description, str):
            raise ValueError("description cannot be empty and must be a string")
        if not isinstance(self.options, list) or not all(isinstance(i, str) for i in self.options):
            raise ValueError("options cannot be empty and must be a list of strings")
        if not self.answer or not isinstance(self.answer, str):
            raise ValueError("answer cannot be empty and must be a string")