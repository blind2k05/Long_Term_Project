import os

# Konfigurasi Path Folder
BASE_DIR = "vault"
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed", "cleaned_docs.jsonl")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

# Pengaturan Model Embedding
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# penggunaan offline
#EMBEDDING_MODEL_NAME = r"D:\Magang\LLM\model_multilingual_offline"
# Parameter RAG
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# Kategori Data
CATEGORIES = ["journal", "school_notes", "coding_notes", "internship_meetings"]