import requests

# Wekan server details
BASE_URL = "http://your-wekan-server/api"
API_KEY = "your-api-key"
BOARD_ID = "your-board-id"
LIST_ID = "your-list-id"

# Set the headers for API calls
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Create a new card
def create_card(title, description):
    url = f"{BASE_URL}/boards/{BOARD_ID}/lists/{LIST_ID}/cards"
    payload = {
        "title": title,
        "description": description,
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("Card created successfully:", response.json())
        return response.json()["_id"]
    else:
        print("Failed to create card:", response.json())
        return None

# Move a card to another list
def move_card(card_id, new_list_id):
    url = f"{BASE_URL}/boards/{BOARD_ID}/cards/{card_id}"
    payload = {
        "listId": new_list_id,
    }
    response = requests.put(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("Card moved successfully:", response.json())
    else:
        print("Failed to move card:", response.json())

# Example usage
if __name__ == "__main__":
    new_card_id = create_card("New Task", "This is a task description.")
    if new_card_id:
        # Replace 'new_list_id' with the actual ID of the target list
        move_card(new_card_id, "new-list-id")
