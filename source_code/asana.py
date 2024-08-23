import json
import requests

# Configuración de Asana
ASANA_ACCESS_TOKEN = 'your_asana_access_token'
WORKSPACE_ID = 'your_workspace_id'  # ID del workspace en Asana

headers = {
    'Authorization': f'Bearer {ASANA_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Leer el archivo JSON
with open('path_to_your_json_file.json', 'r', encoding='utf-8') as file:
    user_stories = json.load(file)

# Crear un nuevo proyecto en Asana
project_name = "User Stories Project"
project_data = {
    "data": {
        "name": project_name,
        "workspace": WORKSPACE_ID,
        "notes": "Project for user stories",
        "public": True
    }
}

response = requests.post(
    'https://app.asana.com/api/1.0/projects',
    headers=headers,
    json=project_data
)

if response.status_code == 201:
    project_id = response.json()['data']['gid']
    print(f"Project '{project_name}' created successfully.")
else:
    print(f"Failed to create project. Response: {response.text}")
    exit()

# Crear tareas en el proyecto para cada historia de usuario
for story in user_stories:
    task_name = story['Name']
    task_notes = f"**ID**: {story['ID']}\n"
    task_notes += f"**Description**: {story['Description']}\n"
    task_notes += f"**Acceptance Criteria**: {story['Acceptance Criteria']}\n"
    task_notes += f"**Story**:\n"
    task_notes += f"  - As a: {story['Story']['As a']}\n"
    task_notes += f"  - I want to: {story['Story']['I want to']}\n"
    task_notes += f"  - So that: {story['Story']['So that']}\n"
    task_notes += f"**Assigned To**: {story['Assigned To']}\n"
    task_notes += f"**Status**: {story['Status']}\n"
    task_notes += f"**Risk**: {story['Risk']}\n"
    task_notes += f"**Release**: {story['Release']}\n"
    task_notes += f"**Tags**: {story['Tags']}\n"
    task_notes += f"**Parent Requirement**: {story['Parent Requirement']}\n"
    task_notes += f"**System ID**: {story['System ID']}\n"
    task_notes += f"**External ID**: {story['External ID']}\n"

    task_data = {
        "data": {
            "name": task_name,
            "notes": task_notes,
            "projects": [project_id]
        }
    }

    response = requests.post(
        'https://app.asana.com/api/1.0/tasks',
        headers=headers,
        json=task_data
    )

    if response.status_code == 201:
        print(f"Task '{task_name}' created successfully.")
    else:
        print(f"Failed to create task '{task_name}'. Response: {response.text}")

print("All user stories have been processed.")
