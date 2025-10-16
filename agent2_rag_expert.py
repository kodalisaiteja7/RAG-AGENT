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
1. Answer questions with HIGH ACCURACY based STRICTLY on the provided context
2. Extract ALL relevant information from the context, even if spread across multiple sources
3. Synthesize information from different sections to provide complete answers
4. Provide detailed explanations with specific examples, numbers, and facts from the context
5. Never make assumptions or add information not present in the context

Response guidelines:
- CAREFULLY READ ALL provided context sources before answering
- Start with a direct, complete answer to the question
- Include ALL relevant details, definitions, steps, examples, and specifics from the context
- If information is in the context, YOU MUST use it - do not say "insufficient data" if the answer exists
- Break down complex information into clear, organized sections
- Quote or paraphrase key information directly from the sources
- If multiple sources provide related information, combine them into a coherent answer
- Only say "I don't have enough information" if the context TRULY lacks the answer

CRITICAL: Your primary goal is ACCURACY. If the answer is in the provided context, you MUST find it and present it completely.
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

        # Filter by relevance threshold - distance < 1.0 is generally good
        # Lower distance = more similar
        RELEVANCE_THRESHOLD = 1.2
        relevant_results = [r for r in results if r.get('distance', 999) < RELEVANCE_THRESHOLD]

        if not relevant_results:
            # If no highly relevant results, use top results anyway
            relevant_results = results[:max(3, len(results) // 2)]

        # Format context
        context_parts = []
        citations = []
        seen_urls = set()

        for idx, result in enumerate(relevant_results):
            metadata = result['metadata']
            content = result['content']
            distance = result.get('distance', 0)

            # Add to context with relevance info
            context_parts.append(f"""
[Source {idx + 1}: {metadata['document_title']} | Relevance: {1 / (1 + distance):.2f}]
{content}
""")

            # Track citations (avoid duplicates)
            url = metadata['url']
            if url not in seen_urls:
                citations.append({
                    "title": metadata['document_title'],
                    "url": url,
                    "source_type": metadata['source_type'],
                    "relevance_score": 1 / (1 + distance)
                })
                seen_urls.add(url)

        context = "\n---\n".join(context_parts)

        # Return all unique citations (dynamic based on relevant sources found)
        return {
            "context": context,
            "citations": citations  # Return all relevant citations dynamically
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
        user_prompt = f"""You have been provided with relevant excerpts from the knowledge base below. Your task is to answer the question using ONLY the information in these excerpts.

Question: {question}

Knowledge Base Context:
{context}

Instructions:
1. Read through ALL the context sources carefully
2. Extract ALL relevant information that answers the question
3. Combine information from multiple sources if needed
4. Provide a complete, detailed answer with specific facts, examples, and explanations
5. If you see the answer directly stated in the context, include it in your response
6. Organize your answer clearly with proper structure
7. Do NOT say information is missing if it's present in the context above

Provide your comprehensive answer now:
"""

        # Step 3: Get response from Grok
        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=3000,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # Lower temperature for more factual, context-focused responses
            )

            answer = response.choices[0].message.content

            # Step 4: Calculate confidence based on relevance scores
            if citations:
                avg_relevance = sum(c.get('relevance_score', 0) for c in citations) / len(citations)
                if avg_relevance >= 0.7 and len(citations) >= 2:
                    confidence = "high"
                elif avg_relevance >= 0.5 or len(citations) >= 1:
                    confidence = "medium"
                else:
                    confidence = "low"
            else:
                confidence = "low"

            # Step 5: Append citations
            if citations:
                citations_text = "\n\n**Sources:**\n"
                for idx, citation in enumerate(citations, 1):
                    citations_text += f"{idx}. [{citation['title']}]({citation['url']})\n"

                answer += citations_text

            return {
                "answer": answer,
                "citations": citations,
                "confidence": confidence
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
