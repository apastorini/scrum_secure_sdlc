import requests
import logging
import os

# Configuraciones de Jira
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
EMAIL = os.getenv('EMAIL')
API_TOKEN =os.getenv('API_TOKEN_JIRA')
PROJECT_KEY = os.getenv('PROJECT_KEY_JIRA_SCRUM')
BOARD_ID = os.getenv('BOARD_ID_JIRA_SCRUM')




# Configuración de logging
log_file_path = os.path.join(os.path.dirname(__file__), 'jira_script.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# URL del archivo JSON en GitHub
GITHUB_URL = 'https://raw.githubusercontent.com/apastorini/scrum_secure_sdlc/main/user_stories/owasp/user_stories.json'


def verificar_token():
    """
    Verifica si el token de Jira sigue vigente realizando una solicitud al endpoint 'myself'.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/myself"
    auth = (EMAIL, API_TOKEN)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        print("El token sigue vigente. Autenticación exitosa.")
        logging.info("El token sigue vigente. Autenticación exitosa.")
        return True
    else:
        print(f"Error de autenticación: {response.status_code} - {response.text}")
        logging.error(f"Error de autenticación: {response.status_code} - {response.text}")
        if response.status_code == 401:
            print("El token no es válido o ha caducado. Genera un nuevo token e intenta de nuevo.")
            logging.error("El token no es válido o ha caducado. Genera un nuevo token e intenta de nuevo.")
        return False


def obtener_tipos_de_issue():
    """
    Obtiene los tipos de issue válidos para el proyecto especificado.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/createmeta?projectKeys={PROJECT_KEY}&expand=projects.issuetypes"
    auth = (EMAIL, API_TOKEN)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        data = response.json()
        tipos_issue = data['projects'][0]['issuetypes']
        print("Tipos de issue disponibles en el proyecto:")
        for tipo in tipos_issue:
            print(f"- {tipo['name']}")
        logging.info(f"Tipos de issue disponibles en el proyecto {PROJECT_KEY}: {[tipo['name'] for tipo in tipos_issue]}")
        return tipos_issue
    else:
        print(f"Error al obtener tipos de issue: {response.status_code} - {response.text}")
        logging.error(f"Error al obtener tipos de issue: {response.status_code} - {response.text}")
        return []


def obtener_historias_de_usuario():
    """
    Obtiene las historias de usuario desde el archivo JSON en GitHub.
    """
    response = requests.get(GITHUB_URL)
    logging.info(f"Solicitando historias de usuario desde {GITHUB_URL}...")
    if response.status_code == 200:
        historias_json = response.json()
        logging.info("Historias de usuario obtenidas exitosamente.")
        return historias_json  # Retorna directamente la lista de historias
    else:
        logging.error(f"Error al obtener el archivo JSON: {response.status_code}")
        return []


def crear_issue(nombre, descripcion, tipo_issue):
    """
    Crea una nueva tarea (issue) en Jira.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (EMAIL, API_TOKEN)
    headers = {
        'Content-Type': 'application/json'
    }
    descripcion_formato = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": descripcion
                    }
                ]
            }
        ]
    }
    payload = {
        'fields': {
            'project': {
                'key': PROJECT_KEY
            },
            'summary': nombre,
            'description': descripcion_formato,
            'issuetype': {
                'name': tipo_issue  # Usar un tipo de issue válido obtenido
            }
        }
    }
    logging.info(f"Creando issue '{nombre}' en el proyecto '{PROJECT_KEY}'...")
    logging.info(f"Payload enviado: {payload}")
    response = requests.post(url, auth=auth, headers=headers, json=payload)
    logging.info(f"Respuesta de la API: {response.status_code} - {response.text}")
    if response.status_code == 201:
        issue_key = response.json()['key']
        print(f"Issue '{nombre}' creado exitosamente con clave: {issue_key}")
        logging.info(f"Issue '{nombre}' creado exitosamente con clave: {issue_key}")
        return issue_key
    else:
        print(f"Error al crear issue '{nombre}': {response.status_code}")
        logging.error(f"Error al crear issue '{nombre}': {response.status_code}")
        logging.error(response.json())
        return None


def main():
    # Verificar si el token es válido antes de continuar
    if not verificar_token():
        print("Por favor, actualiza tu API token y vuelve a ejecutar el script.")
        return

    # Obtener los tipos de issue válidos para el proyecto
    tipos_issue = obtener_tipos_de_issue()
    if not tipos_issue:
        print("No se pudieron obtener los tipos de issue disponibles. Revisa los permisos y la configuración del proyecto.")
        return

    tipo_issue = tipos_issue[0]['name']  # Seleccionar el primer tipo de issue válido como ejemplo

    # Obtener las historias del archivo JSON
    historias = obtener_historias_de_usuario()

    for historia in historias:
        criterios_aceptacion = historia.get('Criterios de Aceptación', '')
        titulo = criterios_aceptacion.split('.')[0].strip()  # Extraer hasta el primer punto como título
        descripcion = f"{historia['Historia']['Como']} {historia['Historia']['Deseo']} {historia['Historia']['Entonces']}"

        issue_key = crear_issue(titulo, descripcion, tipo_issue)

        if issue_key:
            print(f"Issue '{titulo}' creado y movido exitosamente.")


if __name__ == "__main__":
    main()
