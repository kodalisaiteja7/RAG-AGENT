"""Configuration for OneStream Knowledge Agent System"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

# URLs to crawl
ONESTREAM_URLS = [
    "https://www.onestreamsoftware.com/",
    "https://community.onestreamsoftware.com/",
    "https://docs.onestreamsoftware.com/",
]

# Additional sources
SEARCH_QUERIES = [
    "OneStream tutorial",
    "OneStream implementation guide",
    "OneStream business rules VB.NET",
    "OneStream cube views best practices",
    "OneStream dynamic data management",
]

# Crawler settings
MAX_PAGES_PER_DOMAIN = int(os.getenv("MAX_PAGES_PER_DOMAIN", 100))
REQUEST_TIMEOUT = 30
CRAWL_DELAY = 1  # seconds between requests

# Chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Vector DB settings
VECTOR_DB_PATH = "./onestream_vectordb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Knowledge base output
KB_OUTPUT_PATH = "./onestream_kb.json"

# RAG settings
TOP_K_RESULTS = 5
CONTEXT_WINDOW = 3  # Number of chunks to include in context
