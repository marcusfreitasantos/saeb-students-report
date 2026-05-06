from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController

def main():
    dynamodb_client = DynamoDBClient()
    dynamodb_client.db_setup()

    questions_batch = [
        {
            "descriptor": "D1",
            "level": "Fácil",
            "description": "No mapa abaixo, a localização da farmácia é dada pela coordenada (B, 3). [D1_MAPA]\nQual estabelecimento está localizado na coordenada (D, 5)?",
            "options": ["A) Cinema", "B) Hospital", "C) Escola", "D) Supermercado", "E) Padaria"],
            "answer": "B"
        },
        {
            "descriptor": "D1",
            "level": "Médio",
            "description": "Um robô de limpeza percorre uma sala quadrada partindo do canto (1,1). Ele se desloca 4 unidades para a direita e 2 unidades para cima. [D1_ROBO]\nEm quais coordenadas o robô parou?",
            "options": ["A) (5, 3)", "B) (4, 2)", "C) (1, 4)", "D) (5, 2)", "E) (3, 5)"],
            "answer": "A"
        },
        {
            "descriptor": "D1",
            "level": "Médio",
            "description": "No esquema de um cinema, as poltronas são identificadas por uma letra (fila) e um número (coluna). [D1_CINEMA]\nA poltrona de Pedro está na fila E, posição 4. Qual o código da sua poltrona?",
            "options": ["A) 4E", "B) E4", "C) 5D", "D) D5"],
            "answer": "B"
        }
    ]

    question_controller = QuestionController(questions_batch, dynamodb_client)
    question_controller.batch_create()


main()