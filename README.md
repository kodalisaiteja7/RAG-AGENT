# OneStream Knowledge Agent System

A two-agent RAG pipeline that harvests OneStream knowledge and provides expert-level answers using retrieval-augmented generation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  OneStream Knowledge System                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌────────────────────┐        │
│  │   Agent 1:       │         │   Vector Database   │        │
│  │   Knowledge      │────────▶│   (ChromaDB)        │        │
│  │   Harvester      │         │   + Embeddings      │        │
│  │   (GPT-4o)       │         └─────────┬──────────┘        │
│  └──────────────────┘                   │                    │
│         │                               │                    │
│         │ Crawls & Processes            │ Retrieval          │
│         ▼                               ▼                    │
│  ┌──────────────────┐         ┌────────────────────┐        │
│  │  Knowledge Base  │         │   Agent 2:         │        │
│  │  (JSON)          │         │   RAG Expert       │        │
│  │  • Docs          │         │   (Grok-4)         │        │
│  │  • Tutorials     │         │                    │        │
│  │  • Discussions   │         └────────────────────┘        │
│  └──────────────────┘                   │                    │
│                                         │                    │
│                                         ▼                    │
│                              ┌────────────────────┐          │
│                              │  Expert Answers    │          │
│                              │  + Citations       │          │
│                              └────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Features

### Agent 1: Knowledge Harvester
- **Web Crawling**: Crawls OneStream official sites, documentation, and community forums
- **Content Extraction**: Uses Trafilatura for clean content extraction
- **Relevance Filtering**: GPT-4o filters out marketing/irrelevant pages
- **Intelligent Summarization**: Auto-generates summaries for all documents
- **Structured Output**: Produces normalized JSON knowledge base

### Agent 2: RAG Expert Assistant
- **Vector Search**: Fast semantic search using sentence transformers
- **Context Retrieval**: Retrieves top-k relevant chunks for each query
- **Expert Reasoning**: Grok-4 provides detailed, accurate answers
- **Citation System**: Always cites sources with URLs
- **Interactive Mode**: Conversational Q&A interface

## 📦 Installation

### 1. Clone & Install Dependencies

```bash
cd "C:\Users\HARI\Desktop\Teja\OS RAG CLAUDE"
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
```

### 3. Run Initial Setup

```bash
python pipeline.py
```

This will:
1. Crawl OneStream websites
2. Extract and process content
3. Build vector database with embeddings
4. Launch interactive Q&A mode

## 🚀 Usage

### Quick Start

```bash
python pipeline.py
```

### Individual Components

#### 1. Run Knowledge Harvester Only

```bash
python agent1_knowledge_harvester.py
```

Output: `onestream_kb.json`

#### 2. Build Vector Database

```bash
python vector_store.py
```

Requires: `onestream_kb.json`
Output: `./onestream_vectordb/`

#### 3. Query the Expert

```bash
python agent2_rag_expert.py
```

Requires: Vector database

### Programmatic Usage

```python
from pipeline import OneStreamPipeline

# Initialize pipeline
pipeline = OneStreamPipeline()

# Setup (first time only)
pipeline.full_setup()

# Query the system
result = pipeline.query("How do I create business rules in OneStream?")
print(result['answer'])
print(f"Citations: {result['citations']}")

# Interactive mode
pipeline.run_interactive()
```

## 📝 Example Queries

```
Q: How do I configure VIE elimination logic in OneStream?
Q: Explain dynamic data management sequences
Q: What are best practices for building cube views?
Q: Give me a VB.NET business rule example for derived members
Q: How do I implement custom consolidation logic?
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Crawler settings
MAX_PAGES_PER_DOMAIN = 100
CRAWL_DELAY = 1  # seconds

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# RAG settings
TOP_K_RESULTS = 5
CONTEXT_WINDOW = 3
```

## 📂 Project Structure

```
OS RAG CLAUDE/
├── agent1_knowledge_harvester.py  # Agent 1: Crawls & processes knowledge
├── agent2_rag_expert.py           # Agent 2: RAG-based Q&A system
├── vector_store.py                # Vector DB & embedding management
├── pipeline.py                    # Orchestration pipeline
├── config.py                      # Configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
├── README.md                      # This file
├── onestream_kb.json             # Knowledge base (generated)
└── onestream_vectordb/           # Vector database (generated)
```

## 🧠 How It Works

### Phase 1: Knowledge Harvesting
1. Crawls configured OneStream URLs (docs, community, etc.)
2. Discovers linked pages within same domain
3. Extracts clean content using Trafilatura
4. Filters irrelevant pages with GPT-4o
5. Generates summaries for each document
6. Saves structured knowledge base as JSON

### Phase 2: Vector Database Creation
1. Loads knowledge base
2. Chunks documents (1000 tokens with 200 overlap)
3. Generates embeddings using sentence transformers
4. Stores in ChromaDB for fast retrieval

### Phase 3: RAG Question Answering
1. User asks a question
2. Question is embedded and searched in vector DB
3. Top-K relevant chunks are retrieved
4. Context + question sent to Grok-4
5. Expert answer generated with citations
6. Sources provided as clickable links

## 🎓 Advanced Usage

### Force Refresh Knowledge Base

```python
pipeline = OneStreamPipeline()
pipeline.full_setup(force_refresh=True)  # Re-crawl everything
```

### Custom Search Sources

Edit `config.py`:

```python
ONESTREAM_URLS = [
    "https://www.onestreamsoftware.com/",
    "https://community.onestreamsoftware.com/",
    "https://docs.onestreamsoftware.com/",
    "https://your-custom-source.com/"
]
```

### Batch Queries

```python
questions = [
    "How to create business rules?",
    "Best practices for cube views?",
    "VIE elimination setup?"
]

for q in questions:
    result = pipeline.query(q)
    print(f"\nQ: {q}")
    print(f"A: {result['answer']}\n")
```

## 🔍 Models Used

- **Agent 1 (Harvester)**: GPT-4o - Content filtering, summarization
- **Agent 2 (Expert)**: Grok-4 (grok-4-0709) - RAG reasoning and answer generation
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: ChromaDB (persistent local storage)

## 🐛 Troubleshooting

### Issue: "Knowledge base not found"
**Solution**: Run `python agent1_knowledge_harvester.py` first

### Issue: "Vector database not found"
**Solution**: Run `python vector_store.py` after harvesting

### Issue: API rate limits
**Solution**: Adjust `CRAWL_DELAY` in config.py or reduce `MAX_PAGES_PER_DOMAIN`

### Issue: Poor answer quality
**Solution**: Increase `TOP_K_RESULTS` in config.py for more context

## 📊 Performance Tips

1. **First Run**: Takes 10-30 minutes depending on page count
2. **Subsequent Queries**: < 3 seconds per question
3. **Memory**: ~2GB for vector DB with 100 documents
4. **Optimization**: Use GPU for faster embeddings (install `faiss-gpu`)

## 🔐 Security Notes

- Never commit `.env` file with real API keys
- Knowledge base contains publicly available information only
- No authentication credentials are stored

## 📄 License

MIT License - Feel free to modify and use for your projects

## 🤝 Contributing

Suggestions for improvement:
1. Add PDF scraping support
2. Implement incremental updates
3. Add multi-language support
4. Create web UI interface

## 📧 Support

For issues or questions about OneStream itself, visit:
- https://community.onestreamsoftware.com/
- https://docs.onestreamsoftware.com/

---

**Built with Claude Code** 🤖
