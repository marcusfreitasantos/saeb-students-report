from application.questions_usecase import QuestionUseCase

class QuestionController:
    def __init__(self, questions_batch = [], db_client=None):
        self.questions_batch = questions_batch
        self.db_client = db_client


    def create(self, question_data):
        create_question = QuestionUseCase(self.db_client)

        return create_question.build(
            question_data["descriptor"],
            question_data["level"],
            question_data["description"],
            question_data["options"],
            question_data["answer"]
        )
    
    def batch_create(self):
        for batch in self.questions_batch:
            self.create(batch)
        return f'All {str(len(self.questions_batch))} questions sucessfully created.'
    
    def list(self, params):
        questions = QuestionUseCase(self.db_client)
        
        try:
            limit = int((params or {}).get("limit", 10))
            next_token = (params or {}).get("next_token", "")

        except (TypeError, ValueError):
            limit = 10
            next_token = ""

        return questions.list(limit, next_token)

