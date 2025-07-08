import os
import pinecone
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
