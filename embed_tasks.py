from app.clickup_service import get_tasks_from_list
from app.pinecone_service import index
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Your ClickUp list ID
list_id = "901512078802"  # 🔁 Replace if different
tasks = get_tasks_from_list(list_id)

print(f"Fetched {len(tasks)} tasks. Embedding and uploading to Pinecone...")

for task in tasks:
    task_id = task["id"]
    task_name = task["name"]

    if not task_name.strip():
        continue

    # Generate embedding
    response = openai.embeddings.create(
        input=task_name,
        model="text-embedding-3-small"
    )
    vector = response.data[0].embedding

    # Upload to Pinecone
    index.upsert([
        {
            "id": task_id,
            "values": vector,
            "metadata": {
                "name": task_name
            }
        }
    ])

print("✅ All tasks embedded and stored in Pinecone.")
