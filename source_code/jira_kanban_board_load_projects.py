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

# Imprimir las variables de entorno para verificar (no imprimas valores sensibles en un entorno de producción)
logging.info(f"EMAIL: {EMAIL}")
logging.info(f"JIRA_BASE_URL: {JIRA_BASE_URL}")
logging.info(f"PROJECT_KEY: {PROJECT_KEY}")
logging.info(f"API_TOKEN_JIRA: {API_TOKEN_JIRA[:4]}... (token oculto para seguridad)")

def verificar_autenticacion():
    """
    Verifica si el token de API y el correo electrónico son válidos.
    """
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
    """
    Obtiene la lista de tableros disponibles para el proyecto especificado.
    """
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
    elif response.status_code == 401:
        logging.error("Error de autenticación al intentar obtener los tableros. Verifica el token de API y el correo electrónico.")
    else:
        logging.error(f"Error al obtener los tableros: {response.status_code} - {response.text}")
    return []

def main():
    # Obtener y mostrar los tableros disponibles
    tableros = obtener_tableros()
    if not tableros:
        logging.error("No se encontraron tableros disponibles. Asegúrate de que la autenticación sea correcta.")
        return

    # Mostrar los tableros y permitir selección
    for i, tablero in enumerate(tableros, start=1):
        print(f"{i}. {tablero['name']} (ID: {tablero['id']})")

    seleccion = input("Selecciona el número del tablero para continuar, o presiona 'q' para salir: ")
    if seleccion.lower() == 'q':
        logging.info("Proceso terminado por el usuario.")
        return

    try:
        tablero_seleccionado = tableros[int(seleccion) - 1]
        logging.info(f"Tablero seleccionado: {tablero_seleccionado['name']} (ID: {tablero_seleccionado['id']})")
        # Aquí puedes continuar con las operaciones en el tablero seleccionado
    except (IndexError, ValueError):
        logging.error("Selección inválida. Por favor, selecciona un número de la lista.")

if __name__ == "__main__":
    main()
