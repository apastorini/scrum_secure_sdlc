import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuraciones de Trello
API_KEY = os.getenv('API_KEY_TRELLO')
SECRET_API_KEY = os.getenv('SECRET_API_KEY_TRELLO')
TRELLO_BOARD_URL = os.getenv('TRELLO_BOARD_URL')

# URL del archivo JSON en GitHub
GITHUB_URL = 'https://raw.githubusercontent.com/apastorini/scrum_secure_sdlc/main/user_stories/owasp/user_stories.json'


def obtener_token():
    """
    Genera una URL para obtener el Token de Trello y muestra la URL para que el usuario autorice.
    """
    auth_url = f"https://trello.com/1/authorize?expiration=never&name=YourAppName&scope=read,write&response_type=token&key={API_KEY}"
    print("Por favor visita esta URL para autorizar la aplicación y obtener el Token de Trello:")
    print(auth_url)
    token = input("Ingresa el Token de Trello aquí después de autorizar: ")
    return token


def obtener_id_tablero(trello_url):
    """
    Extrae el ID del tablero desde la URL de Trello.
    """
    return trello_url.split('/b/')[1].split('/')[0]


def listar_listas_en_tablero(id_tablero, token):
    """
    Lista todas las listas en un tablero de Trello.
    """
    url = f"https://api.trello.com/1/boards/{id_tablero}/lists"
    params = {
        'key': API_KEY,
        'token': token
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        listas = response.json()
        for index, lista in enumerate(listas):
            print(f"{index + 1}. {lista['name']} (ID: {lista['id']})")
        return listas
    else:
        print(f"Error al obtener las listas: {response.status_code}")
    return []


def obtener_historias_de_usuario():
    """
    Obtiene las historias de usuario desde el archivo JSON en GitHub.
    """
    response = requests.get(GITHUB_URL)
    if response.status_code == 200:
        historias_json = response.json()
        return historias_json  # Retorna directamente la lista de historias
    else:
        print(f"Error al obtener el archivo JSON: {response.status_code}")
        return []


def obtener_tarjetas_en_lista(id_lista, token):
    """
    Obtiene todas las tarjetas en una lista de Trello.
    """
    url = f"https://api.trello.com/1/lists/{id_lista}/cards"
    params = {
        'key': API_KEY,
        'token': token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener tarjetas en la lista: {response.status_code}")
        return []


def eliminar_tarjeta(id_tarjeta, token):
    """
    Elimina una tarjeta de Trello.
    """
    url = f"https://api.trello.com/1/cards/{id_tarjeta}"
    params = {
        'key': API_KEY,
        'token': token
    }
    response = requests.delete(url, params=params)
    if response.status_code == 200:
        print(f"Tarjeta con ID '{id_tarjeta}' eliminada exitosamente.")
    else:
        print(f"Error al eliminar la tarjeta con ID '{id_tarjeta}': {response.status_code}")


def agregar_tarjeta_a_trello(nombre, descripcion, id_lista, token):
    """
    Agrega una tarjeta a una lista en Trello.
    """
    url = f"https://api.trello.com/1/cards"
    query = {
        'key': API_KEY,
        'token': token,
        'idList': id_lista,
        'name': nombre,
        'desc': descripcion
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        tarjeta = response.json()
        print(f"Tarjeta '{nombre}' agregada exitosamente.")
        return tarjeta['id']  # Retorna el ID de la tarjeta
    else:
        print(f"Error al agregar tarjeta '{nombre}': {response.status_code}")
        return None


def agregar_checklist_a_tarjeta(id_tarjeta, nombre_checklist, items, token):
    """
    Agrega un checklist a una tarjeta de Trello.
    """
    url = f"https://api.trello.com/1/cards/{id_tarjeta}/checklists"
    params = {
        'key': API_KEY,
        'token': token,
        'name': nombre_checklist
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        checklist_id = response.json()['id']
        for item in items:
            agregar_item_a_checklist(checklist_id, item, token)
        print(f"Checklist '{nombre_checklist}' agregado a la tarjeta con ID '{id_tarjeta}'.")
    else:
        print(f"Error al agregar checklist a la tarjeta '{id_tarjeta}': {response.status_code}")


def agregar_item_a_checklist(id_checklist, nombre_item, token):
    """
    Agrega un ítem a un checklist en Trello.
    """
    url = f"https://api.trello.com/1/checklists/{id_checklist}/checkItems"
    params = {
        'key': API_KEY,
        'token': token,
        'name': nombre_item,
        'checked': 'false'
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        print(f"Ítem '{nombre_item}' agregado al checklist con ID '{id_checklist}'.")
    else:
        print(f"Error al agregar ítem al checklist con ID '{id_checklist}': {response.status_code}")


def main():
    token = obtener_token()
    id_tablero = obtener_id_tablero(TRELLO_BOARD_URL)
    listas = listar_listas_en_tablero(id_tablero, token)

    if not listas:
        print("No se encontraron listas en el tablero o hubo un error en la autenticación.")
        return

    try:
        seleccion = int(input("Selecciona el número de la lista a la que deseas agregar tarjetas: "))
        id_lista = listas[seleccion - 1]['id']
    except (IndexError, ValueError):
        print("Selección no válida.")
        return

    # Obtener las tarjetas existentes en la lista
    tarjetas_existentes = obtener_tarjetas_en_lista(id_lista, token)
    if tarjetas_existentes:
        decision = input("La lista ya tiene tarjetas. ¿Quieres eliminarlas antes de agregar nuevas? (s/n): ").lower()
        if decision == 's':
            for tarjeta in tarjetas_existentes:
                eliminar_tarjeta(tarjeta['id'], token)

    # Obtener las historias del archivo JSON
    historias = obtener_historias_de_usuario()
    for historia in historias:
        criterios_aceptacion = historia.get('Criterios de Aceptación', '')
        titulo = criterios_aceptacion.split('.')[0].strip()  # Extraer hasta el primer punto como título
        descripcion = f"{historia['Historia']['Como']} {historia['Historia']['Deseo']} {historia['Historia']['Entonces']}"

        id_tarjeta = agregar_tarjeta_a_trello(titulo, descripcion, id_lista, token)

        if id_tarjeta:
            # Crear checklist de criterios de aceptación usando oraciones completas
            items_checklist = [item.strip() for item in criterios_aceptacion.split('.') if item.strip()]
            agregar_checklist_a_tarjeta(id_tarjeta, 'Criterios de Aceptación', items_checklist, token)


if __name__ == "__main__":
    main()
