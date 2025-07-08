from app.clickup_service import get_tasks_from_list

# Replace this with your actual ClickUp list ID from URL
list_id = "901512078802"

tasks = get_tasks_from_list(list_id)

for task in tasks:
    print(f"- {task['name']} (ID: {task['id']})")
