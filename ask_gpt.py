import openai
import os
from dotenv import load_dotenv
from app.pinecone_service import index

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_context(query, top_k=5):
    query_vector = embed_text(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    return [match.metadata.get("context", "") for match in results.matches]

def ask_gpt(question, contexts):
    context_text = "\n\n---\n\n".join(contexts)
    prompt = f"""You are an assistant helping summarize project task data from ClickUp.

Using the context below, answer the user's question in a clear, helpful way.

Question: {question}

Context:
{context_text}

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for project status and activity reporting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    while True:
        question = input("\n🧠 Ask a question (or type 'exit' to quit): ").strip()
        if question.lower() == "exit":
            break

        print(f"\n🔍 Searching for: {question}")
        context_chunks = search_context(question)

        if not context_chunks:
            print("No relevant data found.")
            continue

        print("\n🤖 GPT Answer:\n")
        answer = ask_gpt(question, context_chunks)
        print(answer)
