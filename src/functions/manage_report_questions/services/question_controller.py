from application.questions_usecase import CreateQuestionUseCase


class QuestionController:
    def __init__(self, questions_batch, db_client=None):
        self.questions_batch = questions_batch
        self.db_client = db_client


    def create(self, question_data):
        create_question = CreateQuestionUseCase(self.db_client)

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

