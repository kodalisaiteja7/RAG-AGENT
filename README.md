# SmartDoc AI - Multi-User RAG System

A professional enterprise RAG (Retrieval-Augmented Generation) system with multi-user authentication, document management, and AI-powered question answering.

## 🎯 Features

### Multi-User System
- **User Authentication** - Secure login system with admin and user roles
- **Personal Knowledge Bases** - Each user has their own private document collection
- **Admin Management** - User creation, deletion, and monitoring
- **Chat Session History** - Persistent conversation history per user
- **Session Management** - Create, switch, and delete chat sessions

### Document Management
- **PDF Upload** - Upload PDF documents to your personal knowledge base
- **Auto-Processing** - Automatic text extraction and embedding generation
- **Document Library** - View and manage all uploaded documents
- **Real-time Stats** - Track document and chunk counts
- **Remove Documents** - Delete documents and auto-rebuild vector database

### Advanced RAG Pipeline
- **Semantic Chunking** - Sentence-boundary aware chunking preserves context
- **Query Expansion** - Tries multiple query variations for better recall
- **Relevance Filtering** - Dynamic threshold-based chunk selection
- **Dynamic Citations** - Automatic source attribution with relevance scoring
- **Confidence Scoring** - Answer confidence based on retrieval quality

### Modern UI
- **Clean Design** - Professional gradient-based interface
- **Markdown Rendering** - Properly formatted answers with headings, lists, and emphasis
- **Chat Bubbles** - Modern messaging interface with avatars
- **Mobile Responsive** - Works seamlessly on all devices
- **Source Citations** - Expandable source references for each answer

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│              SmartDoc AI - Multi-User System              │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────┐      ┌──────────────────────┐          │
│  │  Streamlit  │      │  User Management     │          │
│  │  Web App    │─────▶│  (SQLite Auth)       │          │
│  └──────┬──────┘      └──────────────────────┘          │
│         │                                                 │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────────────────────────────────┐            │
│  │  Multi-User Vector Store                │            │
│  │  ┌──────────────┐  ┌─────────────────┐ │            │
│  │  │  Admin KB    │  │  User-Specific  │ │            │
│  │  │  (ChromaDB)  │  │  Collections    │ │            │
│  │  └──────────────┘  └─────────────────┘ │            │
│  └────────────────┬────────────────────────┘            │
│                   │                                       │
│                   ▼                                       │
│  ┌───────────────────────────────────┐                  │
│  │     RAG Expert (Grok-4)           │                  │
│  │  • Semantic Search                │                  │
│  │  • Query Expansion                │                  │
│  │  • Context Assembly               │                  │
│  │  • Answer Generation              │                  │
│  └────────────────┬──────────────────┘                  │
│                   │                                       │
│                   ▼                                       │
│         ┌──────────────────┐                             │
│         │  Expert Answers  │                             │
│         │  + Citations     │                             │
│         │  + Confidence    │                             │
│         └──────────────────┘                             │
└──────────────────────────────────────────────────────────┘
```

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/kodalisaiteja7/RAG-AGENT.git
cd "OS RAG DOCLING"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create `.env` file:

```env
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...

# Optional: Customize chunking
CHUNK_SIZE=1500
CHUNK_OVERLAP=400
```

### 4. Initialize Database

```bash
python init_database.py
```

This creates:
- User database with admin account
- Default knowledge base
- User data directories

### 5. Run the Application

```bash
streamlit run app_multiuser.py
```

Access at: `http://localhost:8501`

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

## 🚀 Usage

### For Users

1. **Login** with your credentials
2. **Upload PDFs** via sidebar → "My Documents" → "Upload"
3. **Wait for processing** (automatic embedding generation)
4. **Ask questions** in the chat interface
5. **View sources** by expanding the citations
6. **Create sessions** for different topics with "New Chat"

### For Admins

1. **Login as admin**
2. Access **Admin Panel** tab
3. **Create users** with custom roles
4. **Monitor usage** - see document counts per user
5. **Delete users** when needed
6. **Upload to admin KB** for shared knowledge

### Re-embedding Documents

After system updates that change chunking:

```bash
python reembed_all_documents.py
```

This applies improved chunking to all existing documents.

### Testing Retrieval

Debug what chunks are being retrieved:

```bash
python test_retrieval.py
```

Enter a question to see:
- Retrieved chunk count
- Similarity distances
- Source documents
- Generated answer

## 📝 Configuration

Edit `config.py`:

```python
# Chunking settings
CHUNK_SIZE = 1500          # Words per chunk
CHUNK_OVERLAP = 400        # Word overlap between chunks

# RAG settings
TOP_K_RESULTS = 12         # Chunks to retrieve
CONTEXT_WINDOW = 10        # Max chunks for context

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

Edit `.env`:

```env
# Adjust chunk sizes
CHUNK_SIZE=1500
CHUNK_OVERLAP=400
```

## 📂 Project Structure

```
OS RAG DOCLING/
├── app_multiuser.py              # Main Streamlit application
├── agent2_rag_expert.py          # RAG expert with query expansion
├── multi_user_vector_store.py   # Multi-user vector database
├── user_manager.py               # User authentication system
├── init_database.py              # Database initialization
├── reembed_all_documents.py     # Re-embed existing documents
├── test_retrieval.py            # Debug retrieval performance
├── config.py                     # Configuration settings
├── requirements.txt              # Python dependencies
├── .env                          # API keys (gitignored)
├── onestream_kb.json            # Admin knowledge base
├── onestream_vectordb/          # Admin vector database
└── user_data/                   # User-specific data
    ├── admin/
    │   ├── user_kb.json         # User's documents
    │   ├── chat_sessions.json   # Chat history
    │   └── user_vectordb/       # User's vector DB
    └── [username]/
        └── ...
```

## 🧠 How It Works

### 1. Document Processing
- **Upload**: User uploads PDF via web interface
- **Extract**: PyPDF2 extracts text content
- **Chunk**: Sentence-aware chunking (respects boundaries)
- **Embed**: Generate embeddings with sentence-transformers
- **Store**: Save to user-specific ChromaDB collection

### 2. Question Answering
- **Query**: User asks a question in chat
- **Expand**: Generate query variations (e.g., remove question words)
- **Search**: Semantic search across both admin and user collections
- **Filter**: Apply relevance threshold (distance < 1.5)
- **Rank**: Sort by similarity distance
- **Generate**: Send top chunks to Grok-4 for answer generation
- **Cite**: Attach source documents with relevance scores

### 3. Answer Quality
- **Temperature 0.1**: Factual, context-focused responses
- **Max 3000 tokens**: Comprehensive answers
- **Dynamic citations**: All relevant sources included
- **Confidence scoring**: Based on retrieval quality

## 🔧 Advanced Features

### Sentence-Aware Chunking

Unlike word-based chunking that breaks mid-sentence:
- Respects sentence boundaries
- Maintains semantic coherence
- Better overlap strategy (full sentences)
- Preserves context across chunks

### Query Expansion

Automatically tries variations:
```
Original: "What is Digoxin?"
Variations:
- "What is Digoxin?"
- "is Digoxin"
- "What is Digoxin"
```

Uses the variation with best retrieval results.

### Relevance Filtering

- Distance < 1.5: Highly relevant
- Fallback: Use top 50% if none pass threshold
- Logs distances for debugging

### Multi-User Isolation

- Admin KB: Shared knowledge base (e.g., company docs)
- User KB: Private, per-user document collections
- Both searched simultaneously
- Citations show source (Admin KB vs My Documents)

## 🔍 Models Used

- **LLM**: Grok-4 (grok-4-0709) via xAI API
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: ChromaDB with persistent storage
- **PDF Processing**: PyPDF2
- **Web Framework**: Streamlit

## 🐛 Troubleshooting

### "Insufficient data in knowledge base"

**Causes:**
1. Documents not uploaded
2. Documents uploaded but not embedded
3. Query doesn't match document content

**Solutions:**
```bash
# Check chunk counts
python -c "from multi_user_vector_store import MultiUserVectorStore; vs = MultiUserVectorStore('admin'); print(vs.get_stats())"

# Re-embed documents
python reembed_all_documents.py

# Test retrieval
python test_retrieval.py
```

### Markdown Not Rendering

Ensure `markdown` library is installed:
```bash
pip install markdown>=3.5.0
```

### API Key Errors

Check `.env` file:
```bash
cat .env  # Linux/Mac
type .env  # Windows
```

Verify keys are set:
```python
python -c "import config; print(f'XAI: {bool(config.XAI_API_KEY)}')"
```

### Vector Database Issues

Rebuild from scratch:
```bash
rm -rf onestream_vectordb user_data/*/user_vectordb
python reembed_all_documents.py
```

## 📊 Performance

- **Chunk Generation**: 1500 words/chunk with 400 overlap
- **Retrieval**: Top 12 chunks in <100ms
- **Answer Generation**: 2-5 seconds (depends on Grok-4 API)
- **Storage**: ~1MB per 10 PDF pages
- **Memory**: ~500MB for 1000 chunks

## 🔐 Security

- ✅ Password hashing with bcrypt
- ✅ Session-based authentication
- ✅ User data isolation
- ✅ HTML escaping for user input
- ✅ Markdown rendering only for AI responses
- ⚠️ `.env` is gitignored (never commit API keys)

## 📈 Future Enhancements

- [ ] Multiple file format support (DOCX, TXT, etc.)
- [ ] Bulk document upload
- [ ] Document search and filtering
- [ ] Export chat history
- [ ] API endpoints for programmatic access
- [ ] Custom embedding models
- [ ] Hybrid search (semantic + keyword)
- [ ] Answer rating and feedback

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Areas for improvement:
1. Additional document formats
2. Better chunking strategies
3. Multi-language support
4. Advanced search filters
5. Analytics dashboard

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Use `test_retrieval.py` to debug
- Review logs in the terminal where Streamlit is running
