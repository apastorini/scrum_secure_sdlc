import os
import requests
from dotenv import load_dotenv
import logging

# Configuración del logging para mostrar mensajes detallados
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables de entorno
load_dotenv()

# Asignar variables de entorno
EMAIL = os.getenv('EMAIL')
API_TOKEN_JIRA = os.getenv('API_TOKEN_JIRA')
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
PROJECT_KEY = os.getenv('PROJECT_KEY_JIRA_KANBAN')
GITHUB_URL = os.getenv('GITHUB_URL')

# Imprimir las variables de entorno para verificar (no imprimas valores sensibles en un entorno de producción)
logging.info(f"EMAIL: {EMAIL}")
logging.info(f"JIRA_BASE_URL: {JIRA_BASE_URL}")
logging.info(f"PROJECT_KEY: {PROJECT_KEY}")
logging.info(f"API_TOKEN_JIRA: {API_TOKEN_JIRA[:4]}... (token oculto para seguridad)")
logging.info(f"GITHUB_URL: {GITHUB_URL}")

def verificar_autenticacion():
    url = f"{JIRA_BASE_URL}/rest/api/3/myself"
    auth = (EMAIL, API_TOKEN_JIRA)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        logging.info("Autenticación exitosa. El token sigue vigente.")
        return True
    elif response.status_code == 401:
        logging.error("Error de autenticación: El token de API o el correo electrónico no son válidos.")
        return False
    else:
        logging.error(f"Error desconocido al verificar la autenticación: {response.status_code} - {response.text}")
        return False

def obtener_tableros():
    if not verificar_autenticacion():
        logging.error("No se puede continuar sin una autenticación válida.")
        return []

    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    auth = (EMAIL, API_TOKEN_JIRA)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        tableros = response.json().get('values', [])
        if tableros:
            logging.info(f"Tableros obtenidos: {[(t['id'], t['name']) for t in tableros]}")
        else:
            logging.info("No se encontraron tableros.")
        return tableros
    else:
        logging.error(f"Error al obtener los tableros: {response.status_code} - {response.text}")
    return []

def obtener_columnas(tablero_id):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{tablero_id}/configuration"
    auth = (EMAIL, API_TOKEN_JIRA)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        columnas = response.json().get('columnConfig', {}).get('columns', [])
        logging.info(f"Columnas disponibles en el tablero: {[columna['name'] for columna in columnas]}")
        return columnas
    else:
        logging.error(f"Error al obtener columnas del tablero: {response.status_code} - {response.text}")
        return []

def crear_issues(historias, tablero_id, columna_nombre):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    auth = (EMAIL, API_TOKEN_JIRA)

    tipos_incidente = obtener_tipos_incidente(tablero_id)
    tipo_exitoso = None

    for historia in historias:
        if tipo_exitoso:
            # Usar el tipo exitoso para todas las historias restantes
            tipos_a_probar = [tipo_exitoso]
        else:
            # Probar todos los tipos de incidencia hasta encontrar uno que funcione
            tipos_a_probar = tipos_incidente

        for tipo in tipos_a_probar:
            logging.info(f"Intentando crear issue con tipo de incidencia: {tipo}")
            payload = {
                "fields": {
                    "project": {"key": PROJECT_KEY},
                    "summary": historia['Criterios de Aceptación'][:250],  # Truncar si es necesario
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{"type": "paragraph", "content": [{"type": "text",
                                                                       "text": historia['Historia']['Como'][:250] + ' ' +
                                                                               historia['Historia']['Deseo'][:250]}]}]
                    },
                    "issuetype": {"name": tipo}
                }
            }
            response = requests.post(url, json=payload, auth=auth)
            if response.status_code == 201:
                issue_id = response.json()['id']
                mover_issue_a_columna_por_nombre(issue_id, columna_nombre)
                tipo_exitoso = tipo
                logging.info(f"Issue creado con éxito. Payload enviado: {payload}")
                break  # Detenerse si se crea exitosamente
            else:
                logging.error(
                    f"Error al crear issue '{historia['Criterios de Aceptación']}' con tipo '{tipo}': {response.status_code} - {response.text}")
                if response.status_code != 400:
                    break

def mover_issue_a_columna_por_nombre(issue_id, columna_nombre):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_id}/transitions"
    auth = (EMAIL, API_TOKEN_JIRA)
    transitions_response = requests.get(url, auth=auth)

    if transitions_response.status_code == 200:
        transitions = transitions_response.json()['transitions']
        for transition in transitions:
            if transition['to']['name'] == columna_nombre:
                transition_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_id}/transitions"
                payload = {"transition": {"id": transition['id']}}
                response = requests.post(transition_url, json=payload, auth=auth)
                if response.status_code == 204:
                    logging.info(f"Issue {issue_id} movido a la columna {columna_nombre}.")
                else:
                    logging.error(
                        f"Error al mover issue {issue_id} a la columna {columna_nombre}: {response.status_code} - {response.text}")
                return
    else:
        logging.error(
            f"Error al obtener transiciones del issue {issue_id}: {transitions_response.status_code} - {transitions_response.text}")

def obtener_tipos_incidente(tablero_id):
    url = f"{JIRA_BASE_URL}/rest/api/3/issuetype"
    auth = (EMAIL, API_TOKEN_JIRA)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        tipos = response.json()
        tipos_nombres = [tipo['name'] for tipo in tipos]
        logging.info(f"Tipos de incidencia disponibles: {tipos_nombres}")
        return tipos_nombres
    else:
        logging.error(f"Error al obtener tipos de incidencia: {response.status_code} - {response.text}")
        return []

def main():
    tableros = obtener_tableros()
    if not tableros:
        logging.error("No se encontraron tableros disponibles. Asegúrate de que la autenticación sea correcta.")
        return

    for i, tablero in enumerate(tableros, start=1):
        print(f"{i}. {tablero['name']} (ID: {tablero['id']})")

    seleccion = input("Selecciona el número del tablero para continuar, o presiona 'q' para salir: ")
    if seleccion.lower() == 'q':
        logging.info("Proceso terminado por el usuario.")
        return

    try:
        tablero_seleccionado = tableros[int(seleccion) - 1]
        tablero_id = tablero_seleccionado['id']
        logging.info(f"Tablero seleccionado: {tablero_seleccionado['name']} (ID: {tablero_id})")

        tipo_proyecto = "Kanban"
        logging.info(f"El tipo de proyecto es: {tipo_proyecto}")

        columnas = obtener_columnas(tablero_id)
        for i, columna in enumerate(columnas, start=1):
            print(f"{i}. {columna['name']}")

        columna_seleccionada = input("Selecciona el número de la columna para agregar las historias: ")

        try:
            seleccion_index = int(columna_seleccionada) - 1
            if seleccion_index < 0 or seleccion_index >= len(columnas):
                raise IndexError("Selección fuera de rango")
            columna = columnas[seleccion_index]
            columna_nombre = columna['name']
            logging.info(f"Columna seleccionada: {columna_nombre}")
        except (IndexError, ValueError) as e:
            logging.error(f"Selección de columna inválida. Error: {str(e)}")
            return

        response = requests.get(GITHUB_URL)
        if response.status_code == 200:
            historias = response.json()
            logging.info("Archivo JSON descargado y cargado exitosamente.")
            crear_issues(historias, tablero_id, columna_nombre)
        else:
            logging.error(f"Error al descargar el archivo JSON: {response.status_code} - {response.text}")

    except (IndexError, ValueError) as e:
        logging.error(f"Selección inválida. {str(e)}")

if __name__ == "__main__":
    main()
