# setup_database.py
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Load variables from a .env file
load_dotenv()

def setup_collections():
    """Connects to Qdrant and ensures collections exist."""

    # This script uses a .env file for credentials, NOT st.secrets
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in your .env file.")
        return

    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Logic to create the 'jds1' collection for job descriptions
    try:
        client.get_collection(collection_name="resumes")
        print("-> Collection 'resumes' already exists.")
    except Exception:
        print("-> Collection 'resumes' not found. Creating...")
        client.recreate_collection(
            collection_name="resumes",
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        print("-> Collection 'resumes' created successfully.")

    # You can add logic for other collections like 'resumes' here if needed

if __name__ == "__main__":
    setup_collections()