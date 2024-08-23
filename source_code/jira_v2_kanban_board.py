import requests
import logging

# Configuraciones de Jira
JIRA_BASE_URL = os.getenv('JIRA_API_TOKEN')
EMAIL = os.getenv('JIRA_API_TOKEN')
API_TOKEN =os.getenv('JIRA_API_TOKEN')
PROJECT_KEY = os.getenv('JIRA_API_TOKEN')
BOARD_ID = '2'
COLUMN_NAME = 'Security Backlog'

# Configuración de logging
logging.basicConfig(filename='jira_script.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# URL del archivo JSON en GitHub
GITHUB_URL = 'https://raw.githubusercontent.com/apastorini/scrum_secure_sdlc/main/user_stories/owasp/user_stories.json'


def obtener_historias_de_usuario():
    response = requests.get(GITHUB_URL)
    if response.status_code == 200:
        historias_json = response.json()
        return historias_json
    else:
        logging.error(f"Error al obtener el archivo JSON: {response.status_code}")
        return []


def listar_columnas_tablero():
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{BOARD_ID}/configuration"
    auth = (EMAIL, API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        columnas = response.json().get('columnConfig', {}).get('columns', [])
        return columnas
    else:
        logging.error(f"Error al obtener las columnas del tablero: {response.status_code}")
        return []


def seleccionar_o_crear_columna():
    columnas = listar_columnas_tablero()
    if not columnas:
        print("No se pudieron obtener las columnas del tablero.")
        return None

    columna_opciones = [columna['name'] for columna in columnas]
    columna_opciones.append('Crear nueva columna "Security Backlog"')

    for idx, nombre in enumerate(columna_opciones, 1):
        print(f"{idx}. {nombre}")

    seleccion = int(input("Selecciona el número de la columna o elige la opción para crear una nueva: ").strip())

    if seleccion == len(columna_opciones):  # Última opción es crear nueva columna
        respuesta = input(f"¿Deseas crear la columna '{COLUMN_NAME}'? (s/n): ").strip().lower()
        if respuesta == 's':
            return crear_columna_si_no_existe()
        else:
            print("No se creará la columna. Por favor, selecciona una columna existente.")
            return None
    elif 1 <= seleccion <= len(columnas):
        return columnas[seleccion - 1]['name']
    else:
        print("Selección no válida. Intenta de nuevo.")
        return seleccionar_o_crear_columna()


def crear_columna_si_no_existe():
    logging.info(f"Creando columna '{COLUMN_NAME}' manualmente...")
    print(f"Por favor, crea la columna '{COLUMN_NAME}' manualmente en Jira si no se crea automáticamente.")
    return COLUMN_NAME


def truncar_titulo(titulo, max_length=255):
    if len(titulo) > max_length:
        logging.warning(f"El título '{titulo}' excede los {max_length} caracteres y será truncado.")
        return titulo[:max_length]
    return titulo


def crear_issue(nombre, descripcion):
    nombre = truncar_titulo(nombre)
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
                'name': 'Iniciativa'
            }
        }
    }
    logging.info(f"Creando issue '{nombre}' en el proyecto '{PROJECT_KEY}'...")
    logging.info(f"Payload enviado: {payload}")
    response = requests.post(url, auth=auth, headers=headers, json=payload)
    logging.info(f"Respuesta de la API: {response.status_code} - {response.text}")
    if response.status_code == 201:
        issue_key = response.json()['key']
        logging.info(f"Issue '{nombre}' creado exitosamente con clave: {issue_key}")
        return issue_key
    else:
        logging.error(f"Error al crear issue '{nombre}': {response.status_code}")
        logging.error(response.json())
        return None


def agregar_comentario(issue_key, comentario):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    auth = (EMAIL, API_TOKEN)
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'body': {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {
                            'type': 'text',
                            'text': comentario
                        }
                    ]
                }
            ]
        }
    }
    logging.info(f"Agregando comentario al issue '{issue_key}': {comentario}")
    response = requests.post(url, auth=auth, headers=headers, json=payload)
    logging.info(f"Respuesta de la API: {response.status_code} - {response.text}")
    if response.status_code == 201:
        logging.info(f"Comentario agregado exitosamente al issue: {issue_key}")
    else:
        logging.error(f"Error al agregar comentario al issue '{issue_key}': {response.status_code}")
        logging.error(response.json())


def obtener_transiciones(issue_key):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = (EMAIL, API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        transiciones = response.json().get('transitions', [])
        return transiciones
    else:
        logging.error(f"Error al obtener transiciones para el issue '{issue_key}': {response.status_code}")
        return []


def mover_issue_a_columna(issue_key, column_name):
    logging.info(f"Intentando mover el issue '{issue_key}' a la columna '{column_name}'...")
    transiciones = obtener_transiciones(issue_key)
    transicion_objetivo = next((t for t in transiciones if t['name'].lower() == column_name.lower()), None)

    if transicion_objetivo:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
        auth = (EMAIL, API_TOKEN)
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'transition': {
                'id': transicion_objetivo['id']
            }
        }
        response = requests.post(url, auth=auth, headers=headers, json=payload)
        if response.status_code == 204:
            logging.info(f"Issue '{issue_key}' movido exitosamente a la columna '{column_name}'.")
        else:
            logging.error(f"Error al mover issue '{issue_key}' a la columna '{column_name}': {response.status_code}")
            logging.error(response.json())
    else:
        logging.error(f"No se encontró una transici\ón para mover a '{column_name}'.")


def main():
    if not verificar_autenticacion():
        print("Token inválido o caducado. Por favor, proporciona un nuevo token.")
        return

    columna_destino = seleccionar_o_crear_columna()
    if not columna_destino:
        print("Proceso terminado debido a la ausencia de la columna deseada.")
        return

    historias = obtener_historias_de_usuario()

    for historia in historias:
        criterios_aceptacion = historia.get('Criterios de Aceptación', '')
        titulo = criterios_aceptacion.split('.')[0].strip()
        descripcion = f"{historia['Historia']['Como']} {historia['Historia']['Deseo']} {historia['Historia']['Entonces']}"
        comentario = f"Criterio de Aceptación:\n{criterios_aceptacion}"

        issue_key = crear_issue(titulo, descripcion)
        if issue_key:
            agregar_comentario(issue_key, comentario)
            mover_issue_a_columna(issue_key, columna_destino)


def verificar_autenticacion():
    url = f"{JIRA_BASE_URL}/rest/auth/1/session"
    auth = (EMAIL, API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        logging.info("El token sigue vigente. Autenticación exitosa.")
        return True
    else:
        logging.error("Token de autenticación inválido o caducado.")
        return False


if __name__ == "__main__":
    main()
