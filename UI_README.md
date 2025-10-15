# Regulatory Agent RAG - Web UI

A Streamlit-based web interface for the Regulatory Agent RAG system.

## Features

- **Chat Interface**: Interactive chat to ask questions about regulations and federal appropriations law
- **PDF Upload**: Add new PDF documents to the knowledge base in real-time
- **Source Citations**: View sources and confidence scores for each answer
- **Knowledge Base Stats**: Monitor document count and vector database statistics
- **Chat History**: Persistent chat history during your session

## Prerequisites

Make sure you have:
1. Python 3.8 or higher installed
2. All dependencies from `requirements.txt` installed
3. Knowledge base (`onestream_kb.json`) and vector database (`onestream_vectordb`) set up
4. API keys configured in `.env` file

## Installation

1. Install Streamlit (if not already installed):
```bash
pip install streamlit
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Running the UI

Launch the Streamlit app:

```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

## Using the UI

### Asking Questions

1. Type your question in the chat input at the bottom of the page
2. Press Enter or click the send button
3. View the answer along with:
   - Confidence score (High/Medium/Low)
   - Source citations with document titles and URLs

### Adding PDF Documents

1. Go to the sidebar on the left
2. Click "Browse files" under "Add Documents"
3. Select a PDF file from your computer
4. Click "Add to Knowledge Base"
5. Wait for processing (this rebuilds the vector database)
6. The new document is now searchable!

### Viewing Statistics

The sidebar shows:
- Total number of documents in the knowledge base
- Breakdown by source type
- Total number of vector chunks indexed

### Clearing Chat

Click "Clear Chat History" in the sidebar to start a fresh conversation.

## Configuration

The UI uses the same configuration as the rest of the system:

- `config.py` - Adjust chunk size, top-k results, etc.
- `.env` - API keys for OpenAI and xAI (Grok)

## Troubleshooting

### "Vector database not found"
Run this to build the vector database:
```bash
python vector_store.py
```

### "Knowledge base not found"
Make sure you have documents loaded:
```bash
python load_regulations_dataset.py
```
Or run the full pipeline:
```bash
python pipeline.py
```

### UI not loading
Check that all dependencies are installed:
```bash
pip install -r requirements.txt
```

### PDF upload fails
- Ensure the PDF is readable (not password-protected or corrupted)
- Check that the PDF contains extractable text (not just images)
- Verify sufficient disk space for vector database

## Features in Detail

### Real-time PDF Processing
When you upload a PDF:
1. Text is extracted from all pages
2. Document is added to `onestream_kb.json`
3. Vector database is automatically rebuilt
4. RAG system reloads with new data
5. Document is immediately searchable

### Chat History
- Persists within your browser session
- Each message shows the question, answer, and sources
- Can be cleared with the sidebar button

### Confidence Scores
- **High**: Multiple relevant sources found
- **Medium**: Limited sources or partial information
- **Low**: Insufficient data in knowledge base

## Advanced Usage

### Running on a Different Port
```bash
streamlit run app.py --server.port 8080
```

### Running on Network
```bash
streamlit run app.py --server.address 0.0.0.0
```

### Customizing Theme
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## Architecture

```
User Query
    ↓
Streamlit UI (app.py)
    ↓
OneStreamExpert (agent2_rag_expert.py)
    ↓
VectorStore (vector_store.py)
    ↓
ChromaDB (onestream_vectordb/)
    ↓
Response with Citations
```

## Support

For issues or questions:
- Check the main project README
- Review configuration settings
- Ensure all dependencies are up to date
