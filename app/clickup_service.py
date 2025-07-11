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
        print("❌ Failed to fetch tasks:", response.status_code, response.text)
        return []

def get_task_details(task_id: str):
    """Fetch detailed task info by task ID."""
    url = f"{BASE_URL}/task/{task_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch task details for {task_id} ({response.status_code})")
        return None

def get_task_comments(task_id: str):
    """Fetch comments on a task."""
    url = f"{BASE_URL}/task/{task_id}/comment"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("comments", [])
    else:
        print(f"❌ Failed to fetch comments for {task_id} ({response.status_code})")
        return []

def get_team_members():
    """Fetch all team members from ClickUp workspace."""
    url = f"{BASE_URL}/team"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        members = []
        teams = response.json().get("teams", [])
        for team in teams:
            for member in team.get("members", []):
                user = member.get("user", {})
                members.append({
                    "id": user.get("id"),
                    "name": user.get("username") or user.get("email"),
                    "role": member.get("role"),
                })
        return members
    else:
        print("❌ Failed to fetch team members:", response.status_code, response.text)
        return []
