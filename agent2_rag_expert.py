"""
Agent 2: OneStream RAG Expert Assistant
Uses retrieval-augmented generation to answer OneStream questions
"""
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from vector_store import VectorStore
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneStreamExpert:
    """Agent 2: RAG-based expert assistant using Grok-4"""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        # Check for API key
        if not config.XAI_API_KEY:
            raise ValueError(
                "XAI_API_KEY is not set. Please configure your API key in environment variables or .env file."
            )

        # Initialize xAI client for Grok
        try:
            self.client = OpenAI(
                api_key=config.XAI_API_KEY,
                base_url="https://api.x.ai/v1"
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

        # Initialize vector store
        self.vector_store = vector_store or VectorStore()

        # System prompt for expert behavior
        self.system_prompt = """You are an expert knowledge assistant with access to a comprehensive knowledge base.

Your role:
1. Answer questions with high accuracy based on the provided context
2. Provide detailed explanations with examples when relevant
3. Break down complex topics using clear reasoning
4. Cite your sources using URLs from the knowledge base
5. Extract and synthesize information from multiple sources when needed

Response guidelines:
- Start with a direct answer to the question
- Provide comprehensive explanations using the context provided
- Include relevant details, definitions, and examples from the source material
- If the context contains the answer but it's spread across multiple sections, synthesize it coherently
- End with "Sources:" section listing the cited references

IMPORTANT: If the provided context contains relevant information, use it to answer the question fully.
Only say "Insufficient data in knowledge base" if the context truly lacks the necessary information to answer.
Do not refuse to answer if the information is present in the context, even if it requires synthesis.
"""

    def retrieve_context(self, query: str, top_k: int = config.TOP_K_RESULTS) -> Dict:
        """
        Retrieve relevant context from vector database
        Returns formatted context and citations
        """
        logger.info(f"Retrieving context for: {query}")

        # Search vector store
        results = self.vector_store.search(query, top_k=top_k)

        if not results:
            return {"context": "", "citations": []}

        # Format context
        context_parts = []
        citations = []
        seen_urls = set()

        for idx, result in enumerate(results):
            metadata = result['metadata']
            content = result['content']

            # Add to context
            context_parts.append(f"""
[Source {idx + 1}: {metadata['document_title']}]
{content}
""")

            # Track citations (avoid duplicates)
            url = metadata['url']
            if url not in seen_urls:
                citations.append({
                    "title": metadata['document_title'],
                    "url": url,
                    "source_type": metadata['source_type']
                })
                seen_urls.add(url)

        context = "\n---\n".join(context_parts)

        return {
            "context": context,
            "citations": citations[:3]  # Top 3 unique sources
        }

    def rank_and_filter_context(self, query: str, retrieved_chunks: List[Dict]) -> List[Dict]:
        """
        Optional: Re-rank retrieved chunks for better relevance
        Currently uses distance-based ranking from vector search
        """
        # Sort by distance (lower is better)
        ranked = sorted(retrieved_chunks, key=lambda x: x.get('distance', float('inf')))
        return ranked[:config.CONTEXT_WINDOW]

    def answer_question(self, question: str, model: str = "grok-4-0709") -> Dict:
        """
        Answer a question using RAG pipeline
        Returns: {answer, citations, confidence}
        """
        logger.info(f"Processing question: {question}")

        # Step 1: Retrieve relevant context
        retrieval_result = self.retrieve_context(question)
        context = retrieval_result['context']
        citations = retrieval_result['citations']

        if not context:
            return {
                "answer": "Insufficient data in knowledge base. Please try rephrasing your question or provide more context.",
                "citations": [],
                "confidence": "low"
            }

        # Step 2: Build prompt with context
        user_prompt = f"""Based on the following knowledge base excerpts, answer this question:

Question: {question}

Knowledge Base Context:
{context}

Provide a comprehensive answer with specific details, examples, and explanations.
Use all relevant information from the context to fully address the question.
"""

        # Step 3: Get response from Grok
        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )

            answer = response.choices[0].message.content

            # Step 4: Append citations
            if citations:
                citations_text = "\n\n**Sources:**\n"
                for idx, citation in enumerate(citations, 1):
                    citations_text += f"{idx}. [{citation['title']}]({citation['url']})\n"

                answer += citations_text

            return {
                "answer": answer,
                "citations": citations,
                "confidence": "high" if len(citations) >= 2 else "medium"
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "citations": citations,
                "confidence": "error"
            }

    def interactive_mode(self):
        """Run interactive Q&A session"""
        print("\n" + "="*60)
        print("OneStream RAG Expert Assistant")
        print("="*60)
        print("Ask me anything about OneStream!")
        print("Type 'quit' to exit\n")

        while True:
            question = input("\n> Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question:
                continue

            print("\n[Thinking...]")
            result = self.answer_question(question)

            print("\n" + "="*60)
            print("Answer:\n")
            print(result['answer'])
            print("\n" + "="*60)


def main():
    """Run OneStream Expert Assistant"""
    # Initialize expert
    expert = OneStreamExpert()

    # Test with sample questions
    test_questions = [
        "How do I configure VIE elimination logic in OneStream?",
        "Explain how to implement dynamic data management sequences in OneStream.",
        "What are the best practices for building cube views?",
        "Give me a sample business rule in VB.NET for derived members."
    ]

    print("\n" + "="*70)
    print("OneStream RAG Expert - Testing Mode")
    print("="*70)

    for question in test_questions:
        print(f"\n\n{'='*70}")
        print(f"Q: {question}")
        print(f"{'='*70}\n")

        result = expert.answer_question(question)
        print(result['answer'])
        print(f"\nConfidence: {result['confidence']}")

    # Switch to interactive mode
    print("\n\nSwitching to interactive mode...\n")
    expert.interactive_mode()


if __name__ == "__main__":
    main()
