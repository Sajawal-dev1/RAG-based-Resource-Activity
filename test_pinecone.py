from app.pinecone_service import index

print("✅ Connected to Pinecone index:", index.describe_index_stats())
