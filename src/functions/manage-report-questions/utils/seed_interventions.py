import json
from pathlib import Path

from infrastructure.dynamodb_repository import DynamoDBClient
from services.intervention_controller import InterventionController


BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "mocks" / "intervencoes_saeb.json"


def seed_interventions_table():
    dynamodb_client = DynamoDBClient()

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
            new_json_data = []
            

            for intervention in data["eixos_saeb"]:                
                for details in intervention["descritores"]:
                    new_intervention_details = []
                    
                    for detail in details["intervencoes"]:
                        new_intervention_details.append( {
                                "type": detail["tipo"],
                                "title": detail["titulo"],
                                "challenge": detail["desafio_robotica"],
                                "integration": detail["integracao_ia"]
                        })

                    new_intervention = {
                        "descriptor": details["id"],
                        "category": intervention["eixo"],
                        "skill": details["habilidade"],
                        "intervention_data": new_intervention_details,
                    }

                    new_json_data.append(new_intervention)

            print("json found")
            print(f"Starting ingestion process of {len(new_json_data)} items.")

            intervention_controller = InterventionController(
                new_json_data,
                dynamodb_client
            )

            intervention_controller.batch_create()

    except FileNotFoundError:
        print("Error: The file was not found.")

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")


if __name__ == "__main__":
    seed_interventions_table()