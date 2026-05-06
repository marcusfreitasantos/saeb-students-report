import uuid
from domain.entities.question import Question
from domain.entities.question import DifficultyLevel

class CreateQuestionUseCase:

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
        self.repository.save("saeb_questions", new_question)
        return new_question