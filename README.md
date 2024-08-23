# scrum_secure_sdlc
Unir TFM Scrum Secure SDLC

## Execute Trello script
python -m venv venv
python.exe -m pip install --upgrade pip
venv\Scripts\activate
pip install -r requirements.txt

##Enviroment Variables
Must set a .env file with:
API_KEY_TRELLO 
SECRET_API_KEY_TRELLO
TRELLO_BOARD_URL 
JIRA_BASE_URL 
EMAIL 
API_TOKEN_JIRA 
PROJECT_KEY_JIRA 
BOARD_ID_JIRA_KANBAN 
COLUMN_NAME = 'Security Backlog'

##Get API KEY TRELLO and Token
https://docs.adaptavist.com/w4j/latest/quick-configuration-guide/add-sources/how-to-generate-trello-api-key-token
https://trello.com/power-ups/admin/
https://www.merge.dev/blog/trello-api-key
https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-group-cards

## get api token jira
https://id.atlassian.com/manage-profile/security/api-tokens
https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/#get-an-api-token
https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/#Create-an-API-token