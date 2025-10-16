"""
Test retrieval to debug what's happening
"""
from multi_user_vector_store import MultiUserVectorStore
from agent2_rag_expert import OneStreamExpert
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Test as admin user
print("="*70)
print("TESTING RETRIEVAL AS ADMIN USER")
print("="*70)

vector_store = MultiUserVectorStore(username='admin')
stats = vector_store.get_stats()

print(f"\nVector Store Stats:")
print(f"  Admin KB chunks: {stats['admin_chunks']}")
print(f"  User KB chunks: {stats['user_chunks']}")
print(f"  Total chunks: {stats['total_chunks']}")

# Test a simple query
test_query = input("\nEnter a test question: ").strip()

if test_query:
    print(f"\nSearching for: '{test_query}'")
    print("-"*70)

    results = vector_store.search(test_query, top_k=12)

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results[:5], 1):
        print(f"\n[{i}] Distance: {result['distance']:.4f}")
        print(f"    Title: {result['metadata']['document_title']}")
        print(f"    Source: {'Admin KB' if result['metadata'].get('is_admin') else 'User KB'}")
        print(f"    Content preview: {result['content'][:150]}...")

    print("\n" + "="*70)
    print("TESTING WITH RAG EXPERT")
    print("="*70)

    expert = OneStreamExpert(vector_store=vector_store)
    answer_result = expert.answer_question(test_query)

    print(f"\nAnswer:\n{answer_result['answer']}")
    print(f"\nConfidence: {answer_result['confidence']}")
    print(f"Citations: {len(answer_result['citations'])}")
