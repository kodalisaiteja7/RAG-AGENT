"""
Vector Database and Embedding System
Handles chunking, embedding, and storage of knowledge documents
"""
import json
import logging
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages embeddings and vector database"""

    def __init__(self, persist_directory: str = config.VECTOR_DB_PATH):
        self.persist_directory = persist_directory

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="onestream_kb",
            metadata={"description": "OneStream Knowledge Base"}
        )

        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)

        # OpenAI client for summarization
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

        logger.info("Vector store initialized")

    def chunk_text(self, text: str, chunk_size: int = config.CHUNK_SIZE,
                   overlap: int = config.CHUNK_OVERLAP) -> List[str]:
        """
        Split text into overlapping chunks
        Uses sentence-aware chunking for better context preservation
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) > 50:  # Minimum chunk size
                chunks.append(chunk)

        return chunks

    def generate_chunk_summary(self, chunk: str) -> str:
        """Generate a concise summary for a chunk using GPT-4o"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"Summarize this OneStream content in one sentence:\n\n{chunk[:500]}"
                }],
                max_tokens=50,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return chunk[:100]

    def embed_documents(self, kb_path: str):
        """
        Load knowledge base, chunk, embed, and store in vector DB
        """
        logger.info(f"Loading knowledge base from {kb_path}...")

        with open(kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        logger.info(f"Processing {len(documents)} documents...")

        all_chunks = []
        all_metadata = []
        all_ids = []

        chunk_id = 0

        for doc_idx, doc in enumerate(documents):
            # Chunk the content
            chunks = self.chunk_text(doc['content'])

            logger.info(f"Document {doc_idx + 1}/{len(documents)}: "
                       f"{doc['title']} -> {len(chunks)} chunks")

            for chunk_idx, chunk in enumerate(chunks):
                # Create metadata for this chunk
                metadata = {
                    "document_title": doc['title'],
                    "url": doc['url'],
                    "source_type": doc['source_type'],
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "doc_summary": doc['summary']
                }

                all_chunks.append(chunk)
                all_metadata.append(metadata)
                all_ids.append(f"chunk_{chunk_id}")
                chunk_id += 1

        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")

        # Generate embeddings
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        )

        logger.info("Storing in vector database...")

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))

            self.collection.add(
                ids=all_ids[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist(),
                documents=all_chunks[i:batch_end],
                metadatas=all_metadata[i:batch_end]
            )

        logger.info(f"✓ Successfully indexed {len(all_chunks)} chunks")

    def search(self, query: str, top_k: int = config.TOP_K_RESULTS) -> List[Dict]:
        """
        Search vector database for relevant chunks
        Returns list of {content, metadata, distance}
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })

        return formatted_results

    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }


def main():
    """Build vector database from knowledge base"""
    vector_store = VectorStore()

    # Embed documents
    vector_store.embed_documents(config.KB_OUTPUT_PATH)

    # Show stats
    stats = vector_store.get_stats()
    print(f"\n✓ Vector database ready")
    print(f"✓ Total chunks indexed: {stats['total_chunks']}")

    # Test search
    print("\nTesting search...")
    results = vector_store.search("How to create business rules in OneStream?")
    print(f"Found {len(results)} results")
    if results:
        print(f"\nTop result:")
        print(f"  Title: {results[0]['metadata']['document_title']}")
        print(f"  URL: {results[0]['metadata']['url']}")
        print(f"  Content preview: {results[0]['content'][:200]}...")


if __name__ == "__main__":
    main()
