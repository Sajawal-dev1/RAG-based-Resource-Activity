import os
from dotenv import load_dotenv
from app.clickup_service import get_tasks_from_list, get_task_details, get_task_comments
from app.pinecone_service import index
import openai
from datetime import datetime

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your ClickUp list ID
list_id = "901512078802"

# Fetch tasks
tasks = get_tasks_from_list(list_id)
print(f"📦 Found {len(tasks)} tasks to enrich and upload...\n")

def embed_text(text: str) -> list:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

for task in tasks:
    task_id = task["id"]
    task_name = task.get("name", "").strip()

    if not task_name:
        continue

    print(f"🔄 Processing: {task_name} ({task_id})")

    # Fetch task details and comments
    details = get_task_details(task_id)
    comments = get_task_comments(task_id)

    # Safely extract fields
    description = details.get("description", "") if details else ""
    assignees = [a.get("username", "") for a in details.get("assignees", [])] if details else []
    status = details.get("status", {}).get("status", "") if details else ""
    updated_at_unix = int(details.get("date_updated", "0")) / 1000 if details else 0
    updated_at_str = datetime.utcfromtimestamp(updated_at_unix).isoformat() if updated_at_unix else ""

    comment_texts = [c.get("comment_text", "") for c in comments if "comment_text" in c]

    # Build full context
    context = f"""
    TASK: {task_name}
    STATUS: {status}
    ASSIGNEES: {', '.join(assignees)}
    DESCRIPTION: {description}
    COMMENTS:
    {''.join(['- ' + c + '\n' for c in comment_texts])}
    """

    # Embed and upload
    vector = embed_text(context)

    index.upsert([
        {
            "id": task_id,
            "values": vector,
            "metadata": {
                "task_id": task_id,
                "name": task_name,
                "assignees": ", ".join(assignees),
                "updated_at": updated_at_str,
                "context": context,
            }
        }
    ])

print("\n✅ All enriched tasks uploaded to Pinecone!")
