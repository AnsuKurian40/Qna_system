import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Paths
MALAYALAM_DOCS_DIR = BASE_DIR / "malayalam_docs"
VECTOR_DB_DIR = BASE_DIR / "vector_db"
ANSWERS_FILE = BASE_DIR / "answers.txt"

# Embedding model (via Ollama)
EMBEDDING_MODEL = "bge-m3" # Fast for indexing

# Answer generation model (via Ollama) - Fallback
LLM_MODEL = "qwen2.5:7b"

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash" 

USE_GEMINI = True

BATCH_SIZE = 15           # Process 15 chunks at a time (prevents timeout)
EMBEDDING_TIMEOUT = 120 
# Chunking settings for Malayalam
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K_RESULTS = 4

# Ensure directories exist
MALAYALAM_DOCS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Optional: Print config for debugging
if __name__ == "__main__":
    print("✅ Configuration loaded successfully")
    print(f"   Documents folder: {MALAYALAM_DOCS_DIR}")
    print(f"   Using embedding model: {EMBEDDING_MODEL}")
    print(f"   Gemini API key: {'Set' if GEMINI_API_KEY else 'Not set'}")

# Optional: Print config for debugging
if __name__ == "__main__":
    print("✅ Configuration loaded successfully")
    print(f"   Documents folder: {MALAYALAM_DOCS_DIR}")
    print(f"   Using embedding model: {EMBEDDING_MODEL}")
    print(f"   Gemini API key: {'Set' if GEMINI_API_KEY else 'Not set'}")