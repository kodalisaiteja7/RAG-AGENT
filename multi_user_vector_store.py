"""
Multi-User Vector Store
Manages separate vector databases for admin (global) and user-specific documents
"""
import json
import logging
from typing import List, Dict
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiUserVectorStore:
    """Vector store with admin and user-specific collections"""

    def __init__(self, username: str = None):
        self.username = username

        # Initialize embedding model with explicit device handling
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            # Load model with explicit device and trust_remote_code
            self.embedding_model = SentenceTransformer(
                config.EMBEDDING_MODEL,
                device=device,
                trust_remote_code=True
            )
            logger.info(f"Loaded embedding model on {device}")
        except Exception as e:
            logger.warning(f"Failed to load on {device}, trying CPU: {e}")
            # Fallback to CPU with explicit settings
            self.embedding_model = SentenceTransformer(
                config.EMBEDDING_MODEL,
                device="cpu",
                trust_remote_code=True
            )
            logger.info("Loaded embedding model on CPU")

        # Admin vector store (shared)
        self.admin_client = chromadb.PersistentClient(
            path=config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.admin_collection = self.admin_client.get_or_create_collection(
            name="admin_kb",
            metadata={"description": "Admin Knowledge Base"}
        )

        # User vector store (if username provided)
        self.user_collection = None
        if username:
            user_vector_path = f"./user_data/{username}/user_vectordb"
            Path(user_vector_path).mkdir(parents=True, exist_ok=True)

            self.user_client = chromadb.PersistentClient(
                path=user_vector_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.user_collection = self.user_client.get_or_create_collection(
                name=f"user_{username}_kb",
                metadata={"description": f"User {username} Knowledge Base"}
            )

    def chunk_text(self, text: str, chunk_size: int = config.CHUNK_SIZE,
                   overlap: int = config.CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) > 50:
                chunks.append(chunk)

        return chunks

    def embed_admin_documents(self, kb_path: str):
        """Embed admin knowledge base documents"""
        logger.info(f"Loading admin knowledge base from {kb_path}...")

        with open(kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        logger.info(f"Processing {len(documents)} admin documents...")

        all_chunks = []
        all_metadata = []
        all_ids = []
        chunk_id = 0

        for doc_idx, doc in enumerate(documents):
            chunks = self.chunk_text(doc['content'])

            logger.info(f"Document {doc_idx + 1}/{len(documents)}: "
                       f"{doc['title']} -> {len(chunks)} chunks")

            for chunk_idx, chunk in enumerate(chunks):
                metadata = {
                    "document_title": doc['title'],
                    "url": doc['url'],
                    "source_type": doc['source_type'],
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "doc_summary": doc['summary'],
                    "is_admin": True
                }

                all_chunks.append(chunk)
                all_metadata.append(metadata)
                all_ids.append(f"admin_chunk_{chunk_id}")
                chunk_id += 1

        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")

        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        )

        logger.info("Storing in admin vector database...")

        # Clear existing and add new
        self.admin_collection.delete(where={"is_admin": True})

        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))

            self.admin_collection.add(
                ids=all_ids[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist(),
                documents=all_chunks[i:batch_end],
                metadatas=all_metadata[i:batch_end]
            )

        logger.info(f"✓ Successfully indexed {len(all_chunks)} admin chunks")

    def embed_user_documents(self, user_kb_path: str):
        """Embed user-specific documents"""
        if not self.user_collection:
            raise ValueError("No user specified for user documents")

        logger.info(f"Loading user knowledge base from {user_kb_path}...")

        with open(user_kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        if not documents:
            logger.info("No user documents to embed")
            return

        logger.info(f"Processing {len(documents)} user documents...")

        all_chunks = []
        all_metadata = []
        all_ids = []
        chunk_id = 0

        for doc_idx, doc in enumerate(documents):
            chunks = self.chunk_text(doc['content'])

            logger.info(f"User Document {doc_idx + 1}/{len(documents)}: "
                       f"{doc['title']} -> {len(chunks)} chunks")

            for chunk_idx, chunk in enumerate(chunks):
                metadata = {
                    "document_title": doc['title'],
                    "url": doc['url'],
                    "source_type": doc['source_type'],
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "doc_summary": doc['summary'],
                    "is_admin": False,
                    "username": self.username
                }

                all_chunks.append(chunk)
                all_metadata.append(metadata)
                all_ids.append(f"user_{self.username}_chunk_{chunk_id}")
                chunk_id += 1

        if not all_chunks:
            return

        logger.info(f"Generating embeddings for {len(all_chunks)} user chunks...")

        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        )

        logger.info("Storing in user vector database...")

        # Clear existing and add new
        self.user_collection.delete(where={"username": self.username})

        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))

            self.user_collection.add(
                ids=all_ids[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist(),
                documents=all_chunks[i:batch_end],
                metadatas=all_metadata[i:batch_end]
            )

        logger.info(f"✓ Successfully indexed {len(all_chunks)} user chunks")

    def search(self, query: str, top_k: int = config.TOP_K_RESULTS) -> List[Dict]:
        """Search both admin and user knowledge bases"""
        query_embedding = self.embedding_model.encode([query])[0]

        # Search admin collection
        admin_results = self.admin_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []

        # Add admin results
        for i in range(len(admin_results['ids'][0])):
            formatted_results.append({
                "content": admin_results['documents'][0][i],
                "metadata": admin_results['metadatas'][0][i],
                "distance": admin_results['distances'][0][i]
            })

        # Search user collection if available
        if self.user_collection:
            user_results = self.user_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # Add user results
            for i in range(len(user_results['ids'][0])):
                formatted_results.append({
                    "content": user_results['documents'][0][i],
                    "metadata": user_results['metadatas'][0][i],
                    "distance": user_results['distances'][0][i]
                })

        # Sort by distance and return top_k
        formatted_results.sort(key=lambda x: x['distance'])
        return formatted_results[:top_k]

    def get_stats(self) -> Dict:
        """Get statistics for both collections"""
        admin_count = self.admin_collection.count()
        user_count = self.user_collection.count() if self.user_collection else 0

        return {
            "admin_chunks": admin_count,
            "user_chunks": user_count,
            "total_chunks": admin_count + user_count
        }
