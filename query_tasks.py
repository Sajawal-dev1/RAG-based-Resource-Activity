import openai
import os
from dotenv import load_dotenv
from app.pinecone_service import index

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_tasks(query: str, top_k=5):
    print(f"\n🔍 Searching for: {query}\n")

    # Step 1: Embed the query
    query_vector = embed_text(query)

    # Step 2: Query Pinecone
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    # Step 3: Display results
    if not results.matches:
        print("No relevant tasks found.")
        return

    for match in results.matches:
        task_name = match.metadata.get("name", "Unknown Task")
        context = match.metadata.get("context", "")
        score = round(match.score, 3)

        print(f"\n🔹 {task_name} (Score: {score})")
        print("-" * 50)
        print(context.strip()[:800])  # Preview first 800 characters
        print("-" * 50)

if __name__ == "__main__":
    while True:
        user_input = input("\n🧠 Ask a question (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit"]:
            break
        search_tasks(user_input)
