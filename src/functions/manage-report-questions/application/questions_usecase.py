import uuid
from domain.entities.question import Question
from domain.entities.question import DifficultyLevel
from infrastructure.config.settings import settings
import json

class QuestionUseCase:

    questions_table_name = settings.DYNAMO_QUESTIONS_TABLE

    def __init__(self, repository):
        self.repository = repository


    def level_map(self, level: str):
        if(level == "Fácil"): return DifficultyLevel.EASY
        if(level == "Médio"): return DifficultyLevel.MEDIUM
        if(level == "Difícil"): return DifficultyLevel.HARD
        return None

    def build(self, descriptor: str, level: str, description: str, options: list, answer: str):
                
        new_question = Question(
            id=str(uuid.uuid4()),
            descriptor=descriptor,
            level=self.level_map(level),
            description=description,
            options=options,
            answer=answer
        )

        self.repository.save(self.questions_table_name, new_question.to_dict())
        return new_question
    
    def list(self, limit: int, next_token: str): 
        next_token_data = json.loads(next_token) if next_token else {}
        items_found = self.repository.list(self.questions_table_name, limit, next_token_data)
        return items_found