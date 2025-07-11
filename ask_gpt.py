import openai
import os
from dotenv import load_dotenv
from app.pinecone_service import index
from app.clickup_service import get_team_members
from datetime import datetime, timedelta
import re
import dateparser
from dateutil.parser import parse as parse_date

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cache team members to avoid hitting the API repeatedly
TEAM_MEMBERS = get_team_members()
TEAM_NAMES = [member["name"].lower() for member in TEAM_MEMBERS if member.get("name")]

def embed_text(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def parse_date_range_from_question(question: str):
    question = question.lower()
    today = datetime.utcnow()

    if "this week" in question:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=4)
        return start, end

    if "last week" in question:
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=4)
        return start, end

    match = re.search(r"last (\d+) days", question)
    if match:
        days = int(match.group(1))
        end = today
        start = today - timedelta(days=days)
        return start, end

    if "past weekend" in question:
        last_sunday = today - timedelta(days=today.weekday() + 1)
        last_saturday = last_sunday - timedelta(days=1)
        return last_saturday, last_sunday

    match = re.search(r"(on|in) (.+)", question)
    if match:
        parsed = dateparser.parse(match.group(2))
        if parsed:
            start = datetime(parsed.year, parsed.month, parsed.day)
            end = start + timedelta(days=1)
            return start, end

    match = re.search(r"from (.+?) to (.+)", question)
    if match:
        start = dateparser.parse(match.group(1))
        end = dateparser.parse(match.group(2))
        if start and end:
            return start, end

    return None, None

def extract_assignee_from_question(question: str):
    for name in TEAM_NAMES:
        if name in question.lower():
            return name
    return None

def search_and_ask_gpt(question: str, top_k=15):
    print(f"\n🔍 Searching for: {question}\n")

    query_vector = embed_text(question)
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    matches = results.matches or []

    start_date, end_date = parse_date_range_from_question(question)
    if start_date and end_date:
        print(f"📅 Date filter: {start_date.date()} → {end_date.date()}")
        matches = [
            m for m in matches
            if "updated_at" in m.metadata and
               start_date <= parse_date(m.metadata["updated_at"]) <= end_date
        ]
        print(f"✅ Matches after date filter: {len(matches)}")

    assignee = extract_assignee_from_question(question)
    if assignee:
        print(f"👤 Filtering by assignee: {assignee.title()}")
        matches = [
            m for m in matches
            if assignee.lower() in m.metadata.get("context", "").lower()
        ]
        print(f"✅ Matches after assignee filter: {len(matches)}")

    if not matches:
        print("❌ No relevant tasks found.")
        return

    context_blocks = []
    for m in matches:
        name = m.metadata.get("name", "Unnamed Task")
        ctx = m.metadata.get("context", "")[:1000]
        context_blocks.append(f"TASK: {name}\n{ctx}")

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are a helpful assistant. Based on the following task summaries, answer the user's question in a clear and structured format with bullet points or numbered lists where appropriate.

User Question:
{question}

Task Data:
{context}
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful AI assistant trained on ClickUp task data."},
            {"role": "user", "content": prompt}
        ]
    )

    print(f"\n🤖 GPT Answer:\n\n{response.choices[0].message.content.strip()}")

if __name__ == "__main__":
    while True:
        user_input = input("\n🧠 Ask a question (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit"]:
            break
        search_and_ask_gpt(user_input)
