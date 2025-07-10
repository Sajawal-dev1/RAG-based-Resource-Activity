import openai
import os
from dotenv import load_dotenv
from app.pinecone_service import index
from datetime import datetime, timedelta
import re
import dateparser
from dateutil.parser import parse as parse_date  # New: safer date parser

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def parse_date_range_from_question(question: str):
    """Parse phrases like 'this week', 'last week', or 'from July 1 to July 5'."""
    question = question.lower()
    today = datetime.utcnow()

    if "this week" in question:
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=4)  # Friday
        return start, end

    if "last week" in question:
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=4)
        return start, end

    match = re.search(r"from (.+?) to (.+)", question)
    if match:
        start_str = match.group(1)
        end_str = match.group(2)
        start = dateparser.parse(start_str)
        end = dateparser.parse(end_str)
        if start and end:
            return start, end

    return None, None

def search_tasks(query: str, top_k=10):
    print(f"\n🔍 Searching for: {query}\n")

    # Step 1: Embed the query
    query_vector = embed_text(query)

    # Step 2: Query Pinecone
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    matches = results.matches or []

    # Step 3: Optional date filtering
    start_date, end_date = parse_date_range_from_question(query)
    if start_date and end_date:
        print(f"📅 Filtering by date: {start_date.date()} to {end_date.date()}")
        print(f"📊 Total matches BEFORE filter: {len(matches)}")

        filtered = []
        for match in matches:
            updated_at_str = match.metadata.get("updated_at")
            if updated_at_str:
                try:
                    updated_at = parse_date(updated_at_str)
                    if start_date <= updated_at <= end_date:
                        filtered.append(match)
                except Exception as e:
                    print(f"⚠️ Failed to parse: {updated_at_str} → {e}")
        matches = filtered
        print(f"✅ Matches AFTER date filter: {len(matches)}")

    if not matches:
        print("❌ No relevant tasks found.")
        return

    # Step 4: Display matches
    for match in matches:
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
