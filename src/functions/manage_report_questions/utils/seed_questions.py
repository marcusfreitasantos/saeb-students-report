import json
from pathlib import Path

from infrastructure.dynamodb_repository import DynamoDBClient
from services.question_controller import QuestionController


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "mocks" / "banco_saeb.json"


def seed_questions_table():
    dynamodb_client = DynamoDBClient()

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
            new_json_data = []

            for key, value in data.items():
                for question in value:

                    new_question = {
                        "descriptor": key,
                        "level": question["nivel"],
                        "description": question["enunciado"],
                        "options": question["opcoes"],
                        "answer": question["resp"]
                    }

                    new_json_data.append(new_question)

            print("json found")
            print(f"Starting ingestion process of {len(new_json_data)} items.")
            print("first row:", new_json_data[0])

            question_controller = QuestionController(
                new_json_data,
                dynamodb_client
            )

            question_controller.batch_create()

    except FileNotFoundError:
        print("Error: The file was not found.")

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")


if __name__ == "__main__":
    seed_questions_table()