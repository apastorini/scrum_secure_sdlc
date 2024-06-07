import json
import requests

# Configuración de Trello
TRELLO_API_KEY = 'your_trello_api_key'
TRELLO_TOKEN = 'your_trello_token'
BOARD_ID = 'your_trello_board_id'
LIST_ID = 'your_trello_list_id'

# Leer el archivo JSON
with open('path_to_your_json_file.json', 'r', encoding='utf-8') as file:
    user_stories = json.load(file)


# Función para crear una tarjeta en Trello
def create_trello_card(name, desc):
    url = f"https://api.trello.com/1/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN,
        'idList': LIST_ID,
        'name': name,
        'desc': desc
    }
    response = requests.request(
        "POST",
        url,
        params=query
    )
    if response.status_code == 200:
        print(f"Card '{name}' created successfully.")
    else:
        print(f"Failed to create card '{name}'. Response: {response.text}")


# Crear tarjetas para cada historia de usuario
for story in user_stories:
    name = story['Name']
    desc = f"**ID**: {story['ID']}\n"
    desc += f"**Description**: {story['Description']}\n"
    desc += f"**Acceptance Criteria**: {story['Acceptance Criteria']}\n"
    desc += f"**Story**:\n"
    desc += f"  - As a: {story['Story']['As a']}\n"
    desc += f"  - I want to: {story['Story']['I want to']}\n"
    desc += f"  - So that: {story['Story']['So that']}\n"
    desc += f"**Assigned To**: {story['Assigned To']}\n"
    desc += f"**Status**: {story['Status']}\n"
    desc += f"**Risk**: {story['Risk']}\n"
    desc += f"**Release**: {story['Release']}\n"
    desc += f"**Tags**: {story['Tags']}\n"
    desc += f"**Parent Requirement**: {story['Parent Requirement']}\n"
    desc += f"**System ID**: {story['System ID']}\n"
    desc += f"**External ID**: {story['External ID']}\n"

    create_trello_card(name, desc)

print("All user stories have been processed.")
