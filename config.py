import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE_DIR = "vault"
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed", "cleaned_docs.jsonl")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

COLLECTION_NAME = "personal_kb"

EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 200))
TOP_K = int(os.environ.get("TOP_K", 6))

CATEGORIES = ["journal", "school_notes", "coding_notes", "internship_meetings"]
