from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import streamlit as st
import os

# Load local .env file only if it exists
if os.path.exists(".env"):
    load_dotenv()

# Safe getter for secrets — works both locally and on Spaces
def get_secret(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Missing required secret: {key}")
    return value

@st.cache_resource
def get_qdrant_client():
    """
    Initializes and returns a Qdrant client, cached for the app session.
    Works locally with `.env` and on Spaces with Secrets UI.
    """
    lurl = get_secret("QDRANT_URL")
    lapi_key = get_secret("QDRANT_API_KEY").strip()
    
    client = QdrantClient(
        url=lurl,
        api_key=lapi_key,
        prefer_grpc=False
    )
    return client
