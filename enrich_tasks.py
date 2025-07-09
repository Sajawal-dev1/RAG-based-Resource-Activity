from app.clickup_service import get_tasks_from_list, get_task_details, get_task_comments
from app.pinecone_service import index
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your ClickUp list ID
list_id = "901512078802"

# Fetch tasks
tasks = get_tasks_from_list(list_id)
print(f"📦 Found {len(tasks)} tasks to enrich and upload...\n")

def embed_text(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

for task in tasks:
    task_id = task["id"]
    task_name = task.get("name", "").strip()

    # Skip empty names
    if not task_name:
        continue

    print(f"🔄 Processing: {task_name} ({task_id})")

    # Fetch extra info
    details = get_task_details(task_id)
    comments = get_task_comments(task_id)

    description = details.get("description", "") if details else ""
    assignees = [a["username"] for a in details.get("assignees", [])] if details else []
    comment_texts = [c.get("comment_text", "") for c in comments]

    # Build full context string
    context = f"""
    TASK: {task_name}
    ASSIGNEES: {', '.join(assignees)}
    DESCRIPTION: {description}
    COMMENTS:
    {''.join(['- ' + c + '\n' for c in comment_texts])}
    """

    # Embed and upsert
    vector = embed_text(context)

    index.upsert([
        {
            "id": task_id,
            "values": vector,
            "metadata": {
                "name": task_name,
                "context": context
            }
        }
    ])

print("\n✅ All enriched tasks uploaded to Pinecone!")
