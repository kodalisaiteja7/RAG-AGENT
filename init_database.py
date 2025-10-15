"""
Initialize Database for Cloud Deployment
Creates admin knowledge base and vector database if they don't exist
"""
import os
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_admin_kb():
    """Create a sample admin knowledge base for initial deployment"""
    sample_docs = [
        {
            "title": "Welcome to the RAG System",
            "url": "system://welcome",
            "summary": "Welcome document for the RAG system",
            "content": """
            Welcome to the Enterprise RAG System!

            This is a multi-user Retrieval-Augmented Generation (RAG) system that allows you to:
            - Upload PDF documents to create your personal knowledge base
            - Ask questions and get AI-powered answers based on your documents
            - Maintain multiple chat sessions with conversation memory
            - Manage your uploaded documents

            Getting Started:
            1. Upload PDF documents using the sidebar
            2. Wait for the system to process and index them
            3. Start asking questions about your documents
            4. Create new chat sessions for different topics

            Features:
            - Multi-user authentication
            - Separate admin and user knowledge bases
            - Chat session management
            - Document upload and removal
            - Context-aware responses with memory

            For best results:
            - Upload relevant documents before asking questions
            - Be specific in your questions
            - Use follow-up questions in the same session for context
            """,
            "source_type": "system",
            "date_collected": "2025-01-15",
            "metadata": {
                "word_count": 150,
                "category": "system",
                "version": "1.0"
            }
        },
        {
            "title": "How to Use This System",
            "url": "system://usage-guide",
            "summary": "Guide on how to use the RAG system effectively",
            "content": """
            Using the RAG System - Quick Guide

            Document Management:
            - Click "Upload" tab in sidebar to add PDF files
            - Click "Manage" tab to view and remove documents
            - System automatically indexes uploaded documents
            - Each user has their own private document collection

            Asking Questions:
            - Type your question in the chat input
            - The system searches your documents for relevant information
            - AI generates answers based on document content
            - Sources are cited at the end of each response

            Chat Sessions:
            - Click "New Chat" to start a fresh conversation
            - Switch between sessions using the sidebar
            - Each session maintains independent conversation history
            - Delete old sessions you no longer need

            Tips for Better Results:
            - Upload documents before asking questions about them
            - Ask specific, focused questions
            - Use follow-up questions in the same session
            - Check the sources cited in responses
            - Upload additional documents if answers are insufficient
            """,
            "source_type": "system",
            "date_collected": "2025-01-15",
            "metadata": {
                "word_count": 180,
                "category": "tutorial",
                "version": "1.0"
            }
        }
    ]

    kb_path = "./onestream_kb.json"

    # Only create if it doesn't exist
    if not os.path.exists(kb_path):
        logger.info("Creating sample admin knowledge base...")
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(sample_docs, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Created {kb_path} with {len(sample_docs)} sample documents")
        return True
    else:
        logger.info("Admin knowledge base already exists")
        return False


def create_directory_structure():
    """Create necessary directories for the application"""
    directories = [
        "./onestream_vectordb",
        "./user_data",
        "./user_data/admin"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Ensured directory exists: {directory}")

    # Create admin user KB if doesn't exist
    admin_kb_path = "./user_data/admin/user_kb.json"
    if not os.path.exists(admin_kb_path):
        with open(admin_kb_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        logger.info("✓ Created empty admin user KB")


def initialize_vector_database():
    """Initialize vector database with sample documents"""
    try:
        from multi_user_vector_store import MultiUserVectorStore
        import config

        kb_path = config.KB_OUTPUT_PATH

        if os.path.exists(kb_path):
            logger.info("Initializing vector database...")

            # Check if vector DB is empty
            vector_store = MultiUserVectorStore()
            stats = vector_store.get_stats()

            if stats['admin_chunks'] == 0:
                logger.info("Vector database is empty, embedding documents...")
                vector_store.embed_admin_documents(kb_path)
                logger.info("✓ Vector database initialized successfully")
            else:
                logger.info(f"Vector database already has {stats['admin_chunks']} chunks")
        else:
            logger.warning(f"Knowledge base file not found: {kb_path}")

    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        raise


def init_for_deployment():
    """
    Complete initialization for cloud deployment
    Call this at application startup
    """
    logger.info("="*60)
    logger.info("Initializing RAG System for Cloud Deployment")
    logger.info("="*60)

    try:
        # Step 1: Create directory structure
        logger.info("\n[1/3] Creating directory structure...")
        create_directory_structure()

        # Step 2: Create sample knowledge base if needed
        logger.info("\n[2/3] Checking admin knowledge base...")
        kb_created = create_sample_admin_kb()

        # Step 3: Initialize vector database
        logger.info("\n[3/3] Initializing vector database...")
        initialize_vector_database()

        logger.info("\n" + "="*60)
        logger.info("✓ Initialization complete!")
        logger.info("="*60)

        return True

    except Exception as e:
        logger.error(f"\n✗ Initialization failed: {e}")
        logger.error("The system may not work correctly without proper initialization")
        return False


if __name__ == "__main__":
    init_for_deployment()
