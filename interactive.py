"""
Interactive OneStream Q&A Mode
Ask questions and get answers using Grok-4 RAG system
"""
import json
import os
from agent2_rag_expert import OneStreamExpert
from vector_store import VectorStore
import config

# Sample OneStream knowledge for immediate use
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
    },
    {
        "title": "OneStream Workflow Configuration",
        "url": "https://docs.onestreamsoftware.com/workflow",
        "summary": "Setting up and managing workflows in OneStream",
        "content": """
        OneStream Workflows coordinate the data collection, validation, and approval process.

        Workflow Components:
        1. Workflow Profiles: Define the structure and stages
        2. Workflow Units: Individual tasks or certifications
        3. Workflow Channels: Group related units
        4. Workflow Certifications: Approval checkpoints

        Configuration Process:
        1. Define Workflow Profile
           - Set time period and scenario
           - Define entity hierarchy
           - Configure certification levels

        2. Create Workflow Units
           - Assign to specific entities
           - Set deadlines and priorities
           - Define submission criteria

        3. Set Up Security
           - Assign users to workflow roles
           - Configure approval chains
           - Set up delegation rules

        Automation Features:
        - Auto-submit based on rules
        - Email notifications for deadlines
        - Escalation procedures
        - Automatic locks after submission

        Best Practices:
        - Test workflows in non-production first
        - Document approval processes clearly
        - Set realistic deadlines with buffer time
        - Monitor workflow status dashboards
        - Train users on submission procedures
        """,
        "source_type": "documentation",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 140}
    },
    {
        "title": "OneStream Consolidation Engine",
        "url": "https://docs.onestreamsoftware.com/consolidation",
        "summary": "Understanding the consolidation engine and custom consolidation logic",
        "content": """
        The OneStream Consolidation Engine handles multi-level entity consolidations automatically.

        Core Concepts:
        1. Entity Hierarchy: Parent-child relationships defining consolidation paths
        2. Ownership Percentages: Control and ownership calculations
        3. Consolidation Methods: Equity pickup, proportionate consolidation, full consolidation
        4. Elimination Rules: Intercompany transaction removal

        Consolidation Process:
        1. Base Level Data: Input at entity level
        2. Aggregation: Sum up child entities
        3. Ownership Adjustments: Apply ownership percentages
        4. Eliminations: Remove intercompany transactions
        5. Parent Totals: Final consolidated amounts

        Custom Consolidation Rules:
        Use VB.NET business rules to extend consolidation logic:
        - Custom allocation methods
        - Complex elimination scenarios
        - Multi-currency translations
        - Non-standard ownership calculations

        Example Custom Rule:
        Public Function CustomConsolidation(ByVal si As SessionInfo, ByVal api As Object) As Object
            Dim parentEntity As Member = api.Pov.Entity.GetParent()
            Dim childEntities As List(Of Member) = api.Members.GetChildren(parentEntity)

            For Each child In childEntities
                Dim ownership As Decimal = api.Members.GetProperty(child, "Ownership")
                Dim childValue As Decimal = api.Data.GetDataCell(child)
                Dim consolidatedValue As Decimal = childValue * (ownership / 100)
                api.Data.SetDataCell(parentEntity, consolidatedValue)
            Next

            Return "Consolidation Complete"
        End Function

        Performance Optimization:
        - Use parallel processing for large hierarchies
        - Cache member properties
        - Optimize elimination rules
        - Pre-calculate common allocations
        """,
        "source_type": "documentation",
        "date_collected": "2025-01-10",
        "metadata": {"word_count": 180}
    }
]

def setup_kb():
    """Setup knowledge base if needed"""
    if not os.path.exists(config.KB_OUTPUT_PATH):
        print("[Setup] Creating knowledge base...")
        with open(config.KB_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_KB, f, indent=2)
        print(f"[OK] Created knowledge base with {len(SAMPLE_KB)} documents\n")

    if not os.path.exists(config.VECTOR_DB_PATH):
        print("[Setup] Building vector database...")
        vector_store = VectorStore()
        vector_store.embed_documents(config.KB_OUTPUT_PATH)
        print("[OK] Vector database ready\n")

def main():
    """Run interactive Q&A session"""
    print("\n" + "="*70)
    print("OneStream RAG Expert - Interactive Mode (Powered by Grok-4)")
    print("="*70)

    # Setup if needed
    setup_kb()

    # Initialize expert
    print("Initializing expert system...")
    expert = OneStreamExpert()
    print("[OK] System ready!\n")

    print("Ask me anything about OneStream!")
    print("Commands: 'quit' or 'exit' to stop, 'help' for tips\n")

    question_count = 0

    while True:
        try:
            question = input("\n> Your question: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if question.lower() == 'help':
                print("\nTips:")
                print("  - Ask about business rules, cube views, workflows, consolidation")
                print("  - Request VB.NET code examples")
                print("  - Ask for step-by-step guides")
                print("  - Query about best practices")
                continue

            question_count += 1
            print(f"\n[Question #{question_count}] Processing...")

            # Get answer
            result = expert.answer_question(question)

            # Display answer
            print("\n" + "="*70)
            print("ANSWER:")
            print("="*70 + "\n")
            print(result['answer'])
            print("\n" + "="*70)
            print(f"Confidence: {result['confidence']}")
            print("="*70)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit gracefully.")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            print("Please try rephrasing your question.\n")

if __name__ == "__main__":
    main()
