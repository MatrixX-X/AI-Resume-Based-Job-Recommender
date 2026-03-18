import hashlib
import uuid
import streamlit as st
from sentence_transformers import SentenceTransformer
import os

# Import the function to get the Qdrant client
from utils.qdrant_client import get_qdrant_client
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

# Use Streamlit's caching to load the model only once
# utils/embeddings.py
import tempfile # <-- 1. Import the tempfile library

@st.cache_resource
def get_embedding_model():
    """
    Loads and caches the SentenceTransformer model into a writable temporary directory.
    """
    # 2. Define a path inside the system's designated temporary directory
    # temp_dir = tempfile.gettempdir()
    # cache_path = os.path.join(temp_dir, "sentence_transformers_cache")
    
    # # 3. Load the model and tell it where to save files
    # model = SentenceTransformer("all-mpnet-base-v2", cache_folder=cache_path)

    print("--- Loading embedding model from local folder ---")
    model_path = os.path.join("models", "all-mpnet-base-v2")
    return SentenceTransformer(model_path)

# The rest of your file remains the same...

def generate_embedding(text: str) -> list:
    """
    Generates an embedding for a given text using the cached model.
    """
    model = get_embedding_model()
    # Encode the text only ONCE
    embedding = model.encode(text)
    return embedding

def hash_to_uuid(text: str) -> str:
    """
    Creates a deterministic UUID from a string.
    """
    hash_hex = hashlib.sha256(text.strip().lower().encode()).hexdigest()
    return str(uuid.UUID(hash_hex[:32]))

def store_embedding(resume_text: str) -> tuple[bool, str]:
    """
    Generates an embedding for the resume, checks for duplicates,
    and stores it in Qdrant if it's new.

    Returns:
        A tuple (is_new, point_id), where is_new is True if the resume was
        added, and False if it already existed.
    """
    # Get the cached Qdrant client
    client = get_qdrant_client()
    collection_name = "resumes"
    
    # 1. Generate the unique ID and the embedding for the resume
    point_id = hash_to_uuid(resume_text)
    embedding = generate_embedding(resume_text)

    # 2. Check for an existing point using the more efficient 'retrieve' method
    existing_points = client.retrieve(
        collection_name=collection_name,
        ids=[point_id]
    )

    # If the list of existing points is not empty, it means we found a duplicate
    if existing_points:
        print(f"Duplicate resume detected with ID: {point_id}")
        return False, point_id  # Already exists

    # 3. If no duplicate was found, create and upsert the new point
    point = PointStruct(
        id=point_id,
        vector=embedding.tolist(),
        payload={"hash": point_id}  # Store the hash in the payload for filtering
    )

    client.upsert(
        collection_name=collection_name,
        points=[point]
    )

    print(f"New resume stored with ID: {point_id}")
    return True, point_id