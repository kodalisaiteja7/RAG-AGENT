"""
Example Usage Scripts for OneStream Knowledge Agent System
"""

from pipeline import OneStreamPipeline


def example_1_quick_start():
    """Example 1: Quick start - single question"""
    print("\n" + "="*70)
    print("Example 1: Quick Start")
    print("="*70 + "\n")

    pipeline = OneStreamPipeline()

    # Ask a question
    question = "How do I configure VIE elimination logic in OneStream?"
    result = pipeline.query(question)

    print(f"Q: {question}\n")
    print(f"A: {result['answer']}\n")
    print(f"Confidence: {result['confidence']}")


def example_2_batch_queries():
    """Example 2: Process multiple questions in batch"""
    print("\n" + "="*70)
    print("Example 2: Batch Queries")
    print("="*70 + "\n")

    pipeline = OneStreamPipeline()

    questions = [
        "Explain dynamic data management sequences in OneStream",
        "What are best practices for building cube views?",
        "How to create business rules in VB.NET?",
        "What is the consolidation engine in OneStream?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*70}")
        print(f"Question {i}/{len(questions)}: {question}")
        print(f"{'─'*70}\n")

        result = pipeline.query(question)
        print(result['answer'])


def example_3_with_citations():
    """Example 3: Extract and display citations"""
    print("\n" + "="*70)
    print("Example 3: Citations Extraction")
    print("="*70 + "\n")

    pipeline = OneStreamPipeline()

    question = "What are the key components of OneStream platform?"
    result = pipeline.query(question)

    print(f"Q: {question}\n")
    print(f"A: {result['answer']}\n")

    if result['citations']:
        print("\nDetailed Citations:")
        for i, citation in enumerate(result['citations'], 1):
            print(f"\n{i}. {citation['title']}")
            print(f"   URL: {citation['url']}")
            print(f"   Type: {citation['source_type']}")


def example_4_interactive():
    """Example 4: Interactive session"""
    print("\n" + "="*70)
    print("Example 4: Interactive Mode")
    print("="*70 + "\n")

    pipeline = OneStreamPipeline()
    pipeline.run_interactive()


def example_5_setup_from_scratch():
    """Example 5: Complete setup from scratch"""
    print("\n" + "="*70)
    print("Example 5: Full Setup (First Time)")
    print("="*70 + "\n")

    pipeline = OneStreamPipeline()

    # Force complete rebuild
    print("⚠️  This will re-crawl all websites and rebuild the database")
    print("⚠️  This may take 15-30 minutes\n")

    confirm = input("Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        pipeline.full_setup(force_refresh=True)
        print("\n✓ Setup complete!")
    else:
        print("Setup cancelled")


def example_6_vector_search_only():
    """Example 6: Direct vector search without LLM"""
    print("\n" + "="*70)
    print("Example 6: Vector Search Only")
    print("="*70 + "\n")

    from vector_store import VectorStore

    vector_store = VectorStore()

    query = "business rules VB.NET"
    results = vector_store.search(query, top_k=5)

    print(f"Search query: '{query}'")
    print(f"Found {len(results)} results\n")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['metadata']['document_title']}")
        print(f"   URL: {result['metadata']['url']}")
        print(f"   Relevance score: {1 - result['distance']:.3f}")
        print(f"   Preview: {result['content'][:150]}...")


def example_7_knowledge_base_stats():
    """Example 7: View knowledge base statistics"""
    print("\n" + "="*70)
    print("Example 7: Knowledge Base Statistics")
    print("="*70 + "\n")

    import json
    import os
    from vector_store import VectorStore
    import config

    # Load knowledge base
    if os.path.exists(config.KB_OUTPUT_PATH):
        with open(config.KB_OUTPUT_PATH, 'r') as f:
            kb = json.load(f)

        print(f"📚 Knowledge Base Stats:")
        print(f"   Total documents: {len(kb)}")

        # Count by source type
        source_types = {}
        for doc in kb:
            st = doc['source_type']
            source_types[st] = source_types.get(st, 0) + 1

        print(f"\n   By source type:")
        for st, count in source_types.items():
            print(f"     • {st}: {count}")

        # Total words
        total_words = sum(doc['metadata']['word_count'] for doc in kb)
        print(f"\n   Total words: {total_words:,}")
        print(f"   Average words per doc: {total_words // len(kb):,}")

    # Vector DB stats
    vector_store = VectorStore()
    stats = vector_store.get_stats()
    print(f"\n🔍 Vector Database Stats:")
    print(f"   Total chunks indexed: {stats['total_chunks']:,}")


# Menu system
def main():
    """Main menu for examples"""
    examples = {
        "1": ("Quick Start - Single Question", example_1_quick_start),
        "2": ("Batch Queries", example_2_batch_queries),
        "3": ("With Citations", example_3_with_citations),
        "4": ("Interactive Mode", example_4_interactive),
        "5": ("Full Setup (First Time)", example_5_setup_from_scratch),
        "6": ("Vector Search Only", example_6_vector_search_only),
        "7": ("Knowledge Base Stats", example_7_knowledge_base_stats),
    }

    print("\n" + "="*70)
    print("OneStream Knowledge Agent - Example Usage")
    print("="*70 + "\n")

    print("Available examples:\n")
    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")

    print("\n  0. Exit")

    while True:
        choice = input("\nSelect example (0-7): ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        if choice in examples:
            _, func = examples[choice]
            try:
                func()
            except KeyboardInterrupt:
                print("\n\nExample interrupted")
            except Exception as e:
                print(f"\n❌ Error: {e}")

            input("\nPress Enter to continue...")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
