import os
import pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Load Pinecone API key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)

INDEX_NAME = "clickup-tasks"

# Create index if it doesn't exist
if INDEX_NAME not in pinecone_client.list_indexes().names():
    pinecone_client.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Connect to the index
index = pinecone_client.Index(INDEX_NAME)
