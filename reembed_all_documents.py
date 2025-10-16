"""
Re-embed All Documents Script
Applies the improved chunking strategy to all existing documents
"""
import os
import json
import logging
from pathlib import Path
from multi_user_vector_store import MultiUserVectorStore
from user_manager import get_user_manager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reembed_admin_kb():
    """Re-embed the admin knowledge base"""
    logger.info("=" * 70)
    logger.info("RE-EMBEDDING ADMIN KNOWLEDGE BASE")
    logger.info("=" * 70)

    kb_path = config.KB_OUTPUT_PATH

    if not Path(kb_path).exists():
        logger.warning(f"Admin KB not found at {kb_path}. Skipping admin KB.")
        return False

    try:
        # Create vector store with no username for admin
        vector_store = MultiUserVectorStore(username=None)

        # Re-embed with new chunking strategy
        vector_store.embed_admin_documents(kb_path)

        # Get stats
        stats = vector_store.get_stats()
        logger.info(f"✓ Admin KB re-embedded successfully!")
        logger.info(f"  Total admin chunks: {stats['admin_chunks']}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to re-embed admin KB: {e}")
        return False


def reembed_user_kb(username: str):
    """Re-embed a specific user's knowledge base"""
    logger.info(f"\n{'=' * 70}")
    logger.info(f"RE-EMBEDDING USER KB: {username}")
    logger.info("=" * 70)

    user_manager = get_user_manager()
    user_kb_path = user_manager.get_user_kb_path(username)

    if not Path(user_kb_path).exists():
        logger.info(f"  No KB found for user {username}. Skipping.")
        return False

    # Check if user has any documents
    with open(user_kb_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    if not documents:
        logger.info(f"  User {username} has no documents. Skipping.")
        return False

    logger.info(f"  Found {len(documents)} documents for {username}")

    try:
        # Create user-specific vector store
        vector_store = MultiUserVectorStore(username=username)

        # Re-embed with new chunking strategy
        vector_store.embed_user_documents(user_kb_path)

        # Get stats
        stats = vector_store.get_stats()
        logger.info(f"✓ User {username} KB re-embedded successfully!")
        logger.info(f"  Total user chunks: {stats['user_chunks']}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to re-embed KB for user {username}: {e}")
        return False


def reembed_all_users():
    """Re-embed all user knowledge bases"""
    logger.info("\n" + "=" * 70)
    logger.info("RE-EMBEDDING ALL USER KNOWLEDGE BASES")
    logger.info("=" * 70)

    user_manager = get_user_manager()
    users = user_manager.list_users()

    logger.info(f"Found {len(users)} total users")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for user in users:
        username = user['username']

        # Skip admin user for user KB (admin uses admin KB)
        if username == 'admin':
            logger.info(f"\n  Skipping user KB for admin (uses admin KB)")
            skip_count += 1
            continue

        result = reembed_user_kb(username)

        if result:
            success_count += 1
        elif result is False and Path(user_manager.get_user_kb_path(username)).exists():
            fail_count += 1
        else:
            skip_count += 1

    logger.info("\n" + "=" * 70)
    logger.info("USER KB RE-EMBEDDING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"  ✓ Successfully re-embedded: {success_count} users")
    logger.info(f"  - Skipped (no documents): {skip_count} users")
    logger.info(f"  ✗ Failed: {fail_count} users")

    return success_count, skip_count, fail_count


def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("DOCUMENT RE-EMBEDDING TOOL")
    print("Applying improved chunking strategy to all documents")
    print("=" * 70)

    print("\nThis script will:")
    print("1. Re-embed the admin knowledge base with improved chunking")
    print("2. Re-embed all user knowledge bases with improved chunking")
    print("\nThis may take several minutes depending on document count.")

    response = input("\nProceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Cancelled by user.")
        return

    # Track overall results
    admin_success = False
    user_success_count = 0

    # Step 1: Re-embed admin KB
    try:
        admin_success = reembed_admin_kb()
    except Exception as e:
        logger.error(f"Unexpected error during admin KB re-embedding: {e}")

    # Step 2: Re-embed all user KBs
    try:
        user_success_count, user_skip_count, user_fail_count = reembed_all_users()
    except Exception as e:
        logger.error(f"Unexpected error during user KB re-embedding: {e}")
        user_success_count = 0
        user_skip_count = 0
        user_fail_count = 0

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    if admin_success:
        print("✓ Admin KB: Re-embedded successfully")
    else:
        print("✗ Admin KB: Not found or failed")

    print(f"✓ User KBs: {user_success_count} re-embedded successfully")

    if user_skip_count > 0:
        print(f"- User KBs: {user_skip_count} skipped (no documents)")

    if user_fail_count > 0:
        print(f"✗ User KBs: {user_fail_count} failed")

    print("\n" + "=" * 70)
    print("Re-embedding complete! You can now use the app with improved accuracy.")
    print("=" * 70)


if __name__ == "__main__":
    main()
