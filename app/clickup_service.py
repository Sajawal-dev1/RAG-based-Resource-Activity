import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
BASE_URL = "https://api.clickup.com/api/v2"

HEADERS = {
    "Authorization": CLICKUP_TOKEN
}

def get_tasks_from_list(list_id: str):
    """Fetch tasks from a given ClickUp list."""
    url = f"{BASE_URL}/list/{list_id}/task"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        tasks = response.json().get("tasks", [])
        return tasks
    else:
        print("Failed to fetch tasks:", response.status_code, response.text)
        return []
