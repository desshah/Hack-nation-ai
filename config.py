"""
Configuration file for IDP Agent
Contains API keys, model settings, and file paths
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Data files
RAW_DATA_FILE = PROJECT_ROOT / "Virtue Foundation Ghana v0.3 - Sheet1.csv"
ENRICHED_DATA_FILE = PROJECT_ROOT / "vf_ghana_enriched_final.csv"
VECTOR_DB_PATH = OUTPUT_DIR / "vector_db"

# API Keys (load from environment or use default)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Set via: export GROQ_API_KEY=your_key

# Model configurations
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # High quality embeddings
EMBEDDING_MODEL_FALLBACK = "sentence-transformers/all-MiniLM-L6-v2"  # Fast fallback

# Groq models
GROQ_PRIMARY_MODEL = "llama-3.3-70b-versatile"  # Best reasoning
GROQ_FAST_MODEL = "llama-3.1-8b-instant"  # Fast triage/classification
GROQ_EXTRACTION_MODEL = "mixtral-8x7b-32768"  # Good at structured output

# Model parameters
EMBEDDING_BATCH_SIZE = 32
MAX_CONTEXT_LENGTH = 8000  # For LLM context
TEMPERATURE_EXTRACTION = 0.1  # Low for consistent extraction
TEMPERATURE_REASONING = 0.3  # Moderate for planning
TOP_K_RETRIEVAL = 5  # Number of documents to retrieve

# Trust score thresholds
TRUST_THRESHOLD_HIGH = 0.7
TRUST_THRESHOLD_LOW = 0.5

# Confidence score thresholds
CONFIDENCE_EXPLICIT = 1.0
CONFIDENCE_IMPLIED = 0.7
CONFIDENCE_UNCERTAIN = 0.4

# Model configuration dictionary for compatibility
MODEL_CONFIG = {
    'primary': GROQ_PRIMARY_MODEL,
    'fast': GROQ_FAST_MODEL,
    'extraction': GROQ_EXTRACTION_MODEL,
    'embedding': EMBEDDING_MODEL,
    'embedding_fallback': EMBEDDING_MODEL_FALLBACK
}
CONFIDENCE_SUSPICIOUS = 0.2

# Processing settings
CHUNK_SIZE = 1000  # Characters per chunk (we'll use facility-level though)
CHUNK_OVERLAP = 100
CACHE_EMBEDDINGS = True

# Output files
EXTRACTED_CAPABILITIES_FILE = OUTPUT_DIR / "extracted_capabilities.json"
FACILITY_PROFILES_FILE = OUTPUT_DIR / "facility_profiles.json"
REGION_GAPS_FILE = OUTPUT_DIR / "region_gaps.json"
CITATIONS_FILE = OUTPUT_DIR / "citations.json"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = OUTPUT_DIR / "idp_agent.log"
