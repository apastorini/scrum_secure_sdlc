import json
import requests
from msal import ConfidentialClientApplication

# Configuración de Azure AD
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
TENANT_ID = 'your_tenant_id'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPES = ['https://graph.microsoft.com/.default']

# Configuración de Microsoft Teams
TEAM_ID = 'your_team_id'

# Autenticación
app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

token_response = app.acquire_token_for_client(scopes=SCOPES)
access_token = token_response['access_token']

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Leer el archivo JSON
with open('path_to_your_json_file.json', 'r', encoding='utf-8') as file:
    user_stories = json.load(file)

# Crear un nuevo canal en el equipo
channel_name = "User Stories Channel"
channel_data = {
    "displayName": channel_name,
    "description": "Channel for user stories",
    "membershipType": "standard"
}

response = requests.post(
    f'https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/channels',
    headers=headers,
    json=channel_data
)

if response.status_code == 201:
    print(f"Channel '{channel_name}' created successfully.")
    channel_id = response.json()['id']
else:
    print(f"Failed to create channel. Response: {response.text}")
    exit()

# Crear un plan en Planner
planner_plan_name = "User Stories Plan"
planner_plan_data = {
    "owner": TEAM_ID,
    "title": planner_plan_name
}

response = requests.post(
    'https://graph.microsoft.com/v1.0/planner/plans',
    headers=headers,
    json=planner_plan_data
)

if response.status_code == 201:
    print(f"Planner plan '{planner_plan_name}' created successfully.")
    plan_id = response.json()['id']
else:
    print(f"Failed to create Planner plan. Response: {response.text}")
    exit()

# Crear una pestaña de Planner en el nuevo canal
tab_name = "User Stories Board"
tab_data = {
    "displayName": tab_name,
    "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.planner",
    "configuration": {
        "entityId": plan_id,
        "contentUrl": f"https://tasks.office.com/{TENANT_ID}/Home/PlannerFrame?auth_pvr=Orgid&auth_upn={{userPrincipalName}}&usePlanner=1&groupId={TEAM_ID}&planId={plan_id}",
        "removeUrl": None,
        "websiteUrl": None
    }
}

response = requests.post(
    f'https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/channels/{channel_id}/tabs',
    headers=headers,
    json=tab_data
)

if response.status_code == 201:
    print(f"Tab '{tab_name}' created successfully.")
else:
    print(f"Failed to create tab. Response: {response.text}")
    exit()

# Crear tareas en Planner para cada historia de usuario
for story in user_stories:
    task_data = {
        "planId": plan_id,
        "title": story['Name'],
        "bucketId": None,  # Opcional, se puede especificar un bucketId si se desea
        "dueDateTime": None,  # Opcional, se puede especificar una fecha de vencimiento si se desea
        "assignments": {},  # Opcional, se pueden asignar usuarios a la tarea
        "details": {
            "description": f"**Description**: {story['Description']}\n"
                           f"**Acceptance Criteria**: {story['Acceptance Criteria']}\n"
                           f"**Story**:\n"
                           f"  - As a: {story['Story']['As a']}\n"
                           f"  - I want to: {story['Story']['I want to']}\n"
                           f"  - So that: {story['Story']['So that']}\n"
                           f"**Assigned To**: {story['Assigned To']}\n"
                           f"**Status**: {story['Status']}\n"
                           f"**Risk**: {story['Risk']}\n"
                           f"**Release**: {story['Release']}\n"
                           f"**Tags**: {story['Tags']}\n"
                           f"**Parent Requirement**: {story['Parent Requirement']}\n"
                           f"**System ID**: {story['System ID']}\n"
                           f"**External ID**: {story['External ID']}\n"
        }
    }

    response = requests.post(
        'https://graph.microsoft.com/v1.0/planner/tasks',
        headers=headers,
        json=task_data
    )

    if response.status_code == 201:
        print(f"Task '{story['Name']}' created successfully.")
    else:
        print(f"Failed to create task '{story['Name']}'. Response: {response.text}")

print("All user stories have been processed.")
