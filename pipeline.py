"""
Orchestration Pipeline for OneStream Knowledge Agent System
Coordinates Agent 1 (Knowledge Harvester) and Agent 2 (RAG Expert)
"""
import logging
import os
from typing import Optional
from agent1_knowledge_harvester import KnowledgeHarvester
from vector_store import VectorStore
from agent2_rag_expert import OneStreamExpert
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneStreamPipeline:
    """
    Main orchestration pipeline
    Manages the two-agent system workflow
    """

    def __init__(self):
        self.harvester = KnowledgeHarvester()
        self.vector_store = VectorStore()
        self.expert = OneStreamExpert(vector_store=self.vector_store)

    def run_harvester(self, force_refresh: bool = False):
        """
        Execute Agent 1: Knowledge Harvester
        Downloads and processes OneStream knowledge
        """
        kb_exists = os.path.exists(config.KB_OUTPUT_PATH)

        if kb_exists and not force_refresh:
            logger.info(f"Knowledge base already exists at {config.KB_OUTPUT_PATH}")
            logger.info("Use force_refresh=True to rebuild")
            return

        logger.info("\n" + "="*70)
        logger.info("PHASE 1: Knowledge Harvesting")
        logger.info("="*70 + "\n")

        # Harvest knowledge
        documents = self.harvester.harvest(config.ONESTREAM_URLS)

        # Save knowledge base
        self.harvester.save_knowledge_base(config.KB_OUTPUT_PATH)

        logger.info(f"\n✓ Phase 1 complete: {len(documents)} documents harvested")

    def build_vector_db(self, force_rebuild: bool = False):
        """
        Build vector database from knowledge base
        Creates embeddings and indexes documents
        """
        vector_db_exists = os.path.exists(config.VECTOR_DB_PATH)

        if vector_db_exists and not force_rebuild:
            logger.info(f"Vector database already exists at {config.VECTOR_DB_PATH}")
            logger.info("Use force_rebuild=True to rebuild")
            return

        logger.info("\n" + "="*70)
        logger.info("PHASE 2: Vector Database Construction")
        logger.info("="*70 + "\n")

        # Check if knowledge base exists
        if not os.path.exists(config.KB_OUTPUT_PATH):
            raise FileNotFoundError(
                f"Knowledge base not found at {config.KB_OUTPUT_PATH}. "
                "Run harvest phase first."
            )

        # Build vector database
        self.vector_store.embed_documents(config.KB_OUTPUT_PATH)

        stats = self.vector_store.get_stats()
        logger.info(f"\n✓ Phase 2 complete: {stats['total_chunks']} chunks indexed")

    def query(self, question: str) -> dict:
        """
        Execute Agent 2: RAG Expert
        Answer a question using the knowledge base
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 3: Question Answering")
        logger.info("="*70 + "\n")

        # Verify vector DB exists
        if not os.path.exists(config.VECTOR_DB_PATH):
            raise FileNotFoundError(
                f"Vector database not found. Run build_vector_db() first."
            )

        # Get answer from expert
        result = self.expert.answer_question(question)
        return result

    def run_interactive(self):
        """Run interactive Q&A mode"""
        self.expert.interactive_mode()

    def full_setup(self, force_refresh: bool = False):
        """
        Complete pipeline setup
        Runs both harvesting and vector DB creation
        """
        logger.info("\n" + "="*70)
        logger.info("OneStream Knowledge Agent System - Full Setup")
        logger.info("="*70 + "\n")

        # Phase 1: Harvest knowledge
        self.run_harvester(force_refresh=force_refresh)

        # Phase 2: Build vector database
        self.build_vector_db(force_rebuild=force_refresh)

        logger.info("\n" + "="*70)
        logger.info("✓ Setup Complete - System Ready")
        logger.info("="*70 + "\n")


def main():
    """
    Main execution entry point
    """
    pipeline = OneStreamPipeline()

    # Check if setup is needed
    needs_setup = (
        not os.path.exists(config.KB_OUTPUT_PATH) or
        not os.path.exists(config.VECTOR_DB_PATH)
    )

    if needs_setup:
        print("\n[!] Knowledge base not found. Running initial setup...\n")
        pipeline.full_setup()
    else:
        print("\n[OK] Knowledge base found. Ready to answer questions.\n")

    # Start interactive mode
    print("\n" + "="*70)
    print("Starting interactive mode...")
    print("="*70 + "\n")

    pipeline.run_interactive()


if __name__ == "__main__":
    main()
