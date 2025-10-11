"""
Quick Demo Mode - Test RAG system without full crawling
Uses a small sample knowledge base
"""
import json
from agent2_rag_expert import OneStreamExpert
from vector_store import VectorStore
import config

# Sample OneStream knowledge for demo
SAMPLE_KB = [
    {
        "title": "OneStream Business Rules Guide",
        "url": "https://docs.onestreamsoftware.com/business-rules",
        "summary": "Guide to creating and managing business rules in OneStream using VB.NET",
        "content": """
        OneStream Business Rules are written in VB.NET and allow for custom calculations,
        validations, and data transformations. Key concepts include:

        1. Business Rule Types:
           - Member Formula Rules: Calculate derived members
           - Consolidation Rules: Custom consolidation logic
           - Data Quality Rules: Validate data input
           - Dashboard Rules: Custom dashboard calculations

        2. Basic Structure:
        Public Function Main(ByVal si As SessionInfo, ByVal globals As BRGlobals, ByVal api As Object, ByVal args As DashboardExtenderArgs) As Object
            Try
                ' Your business logic here
                Return "Success"
            Catch ex As Exception
                Throw ErrorHandler.LogWrite(si, New XFException(si, ex))
            End Try
        End Function

        3. Common APIs:
           - api.Data.GetDataCell() - Retrieve cell values
           - api.Data.SetDataCell() - Set cell values
           - api.Members.GetMember() - Get member properties
           - api.Pov.GetPov() - Get point of view context

        Best practices: Always use error handling, cache member lookups, and test thoroughly.
        """,
        "source_type": "documentation",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 150}
    },
    {
        "title": "OneStream Cube Views Overview",
        "url": "https://docs.onestreamsoftware.com/cube-views",
        "summary": "Overview of creating and configuring cube views in OneStream",
        "content": """
        Cube Views in OneStream provide multi-dimensional data visualization and reporting.

        Key Components:
        1. Rows: Define vertical dimension (e.g., Accounts)
        2. Columns: Define horizontal dimension (e.g., Time periods)
        3. POV: Point of View dimensions (Scenario, Entity, etc.)
        4. Formatting: Number formats, cell styles, conditional formatting

        Types of Cube Views:
        - Standard Views: Basic multi-dimensional reports
        - Quick Views: Simplified ad-hoc analysis
        - Guided Views: Workflow-integrated reporting

        Best Practices:
        - Limit row/column expansions for performance
        - Use member filters to reduce data volume
        - Implement row/column suppression for zero values
        - Cache frequently accessed views
        - Test with production-scale data volumes

        Advanced Features:
        - Asymmetric reporting
        - Dynamic expansion members
        - Cell-level annotations
        - Drill-through capabilities
        """,
        "source_type": "documentation",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 120}
    },
    {
        "title": "VIE Elimination Configuration",
        "url": "https://community.onestreamsoftware.com/vie-elimination",
        "summary": "How to configure Variable Interest Entity (VIE) elimination logic",
        "content": """
        VIE (Variable Interest Entity) Elimination in OneStream requires careful configuration:

        Step 1: Define VIE Relationships
        - Create custom consolidation members for VIE entities
        - Set up parent-child relationships in entity hierarchy
        - Define elimination accounts in account dimension

        Step 2: Configure Elimination Rules
        - Use Consolidation business rules for VIE logic
        - Implement api.Consolidation.Execute() for custom eliminations
        - Handle intercompany transactions between VIE and primary beneficiary

        Step 3: Testing
        - Verify elimination amounts at parent level
        - Check that VIE contributions are properly consolidated
        - Validate against regulatory requirements

        Example VB.NET Code:
        Dim vieEntity As Member = api.Members.GetMember("VIE_Entity")
        Dim elimAmount As Decimal = api.Data.GetDataCell("ElimAccount")
        api.Data.SetDataCell("ParentEntity", elimAmount * -1)

        Common Issues:
        - Incorrect ownership percentages
        - Missing elimination accounts
        - Circular reference errors in consolidation
        """,
        "source_type": "community",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 145}
    },
    {
        "title": "Dynamic Data Management Sequences",
        "url": "https://docs.onestreamsoftware.com/data-management",
        "summary": "Guide to implementing data management sequences for automated data processing",
        "content": """
        Data Management Sequences automate data integration and transformation workflows.

        Sequence Types:
        1. Import Sequences: Load data from external sources
        2. Export Sequences: Extract data to external systems
        3. Transformation Sequences: Transform and validate data
        4. Consolidation Sequences: Run consolidation processes

        Configuration Steps:
        1. Create Data Source Connection
           - Define connection string
           - Configure authentication
           - Test connectivity

        2. Build Transformation Rules
           - Map source fields to OneStream dimensions
           - Apply business logic transformations
           - Handle data quality checks

        3. Schedule Execution
           - Set frequency (daily, weekly, monthly)
           - Define time windows
           - Configure error notifications

        Best Practices:
        - Use staging tables for large imports
        - Implement incremental loading when possible
        - Log all transformation errors
        - Monitor execution times
        - Archive processed files

        Error Handling:
        - Set up email notifications for failures
        - Implement retry logic for transient errors
        - Maintain audit trails of all data changes
        """,
        "source_type": "documentation",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 155}
    }
]

def create_demo_kb():
    """Create sample knowledge base"""
    print("Creating demo knowledge base...")
    with open(config.KB_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_KB, f, indent=2)
    print(f"[OK] Created {config.KB_OUTPUT_PATH} with {len(SAMPLE_KB)} documents")

def build_demo_vectordb():
    """Build vector database from demo KB"""
    print("\nBuilding vector database...")
    vector_store = VectorStore()
    vector_store.embed_documents(config.KB_OUTPUT_PATH)
    stats = vector_store.get_stats()
    print(f"[OK] Vector database ready with {stats['total_chunks']} chunks")

def run_demo():
    """Run demo with sample questions"""
    print("\n" + "="*70)
    print("OneStream RAG Expert - DEMO MODE")
    print("="*70)
    print("Using sample knowledge base for quick testing\n")

    # Setup demo data
    create_demo_kb()
    build_demo_vectordb()

    # Initialize expert
    expert = OneStreamExpert()

    # Test questions
    test_questions = [
        "How do I configure VIE elimination logic in OneStream?",
        "What are the best practices for building cube views?",
        "Give me a sample business rule in VB.NET for derived members.",
        "Explain dynamic data management sequences"
    ]

    print("\n" + "="*70)
    print("Testing with sample questions...")
    print("="*70)

    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'='*70}")
        print(f"Question {i}/{len(test_questions)}: {question}")
        print(f"{'='*70}\n")

        result = expert.answer_question(question)
        print(result['answer'])
        print(f"\nConfidence: {result['confidence']}")

    # Interactive mode
    print("\n\n" + "="*70)
    print("Entering interactive mode...")
    print("="*70)
    expert.interactive_mode()

if __name__ == "__main__":
    run_demo()
