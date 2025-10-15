# Chat Sessions & Document Management Guide

## New Features Added

### 1. Multiple Chat Sessions
Each user can now create and manage multiple independent chat conversations.

**Features:**
- Create unlimited chat sessions
- Switch between sessions seamlessly
- Each session maintains its own conversation history
- Delete old sessions you no longer need
- Sessions persist across logins

**How to Use:**
1. Click **"➕ New Chat"** in the sidebar to create a new session
2. Click on any session name to switch to it
3. The active session is marked with 📌
4. Click the 🗑️ button to delete a session (except the active one)

### 2. Chat Memory/Context Awareness
The AI now remembers your conversation within each session.

**How it Works:**
- Maintains context from the last 3 exchanges (6 messages)
- Automatically includes previous conversation in new queries
- Provides more coherent, context-aware responses
- Understands follow-up questions and references

**Example:**
```
User: "What is VIE elimination?"
AI: [Explains VIE elimination...]

User: "Can you show me an example?"
AI: [Provides example with context from previous answer]

User: "What are common issues with that?"
AI: [Lists issues related to VIE elimination]
```

### 3. Document Removal
Remove documents you've uploaded to your knowledge base.

**Features:**
- View all uploaded documents with details
- See filename, page count, word count, and upload date
- Remove documents with one click
- Automatic vector database rebuild after removal

**How to Use:**
1. Go to **"📄 My Documents"** in the sidebar
2. Click the **"Manage"** tab
3. Expand any document to see details
4. Click **"🗑️ Remove"** to delete it
5. The document is removed and vector database updates automatically

## UI Layout

### Sidebar Structure
```
├── 💬 Chat Sessions
│   ├── ➕ New Chat
│   └── List of your chat sessions
│
├── 📊 Knowledge Base
│   ├── Admin KB (chunks count)
│   └── My Documents (chunks count)
│
├── 📄 My Documents
│   ├── Upload Tab
│   │   └── Upload PDF files
│   └── Manage Tab
│       └── View and remove documents
│
└── Logout
```

## Data Storage

### Chat Sessions
- Stored in: `user_data/{username}/chat_sessions.json`
- Format: JSON with session metadata and message history
- Persists across application restarts

### Documents
- Stored in: `user_data/{username}/user_kb.json`
- Vector embeddings in: `user_data/{username}/user_vectordb/`
- Automatically indexed and searchable

## Technical Details

### Chat Memory Implementation
- Includes last 6 messages (3 exchanges) as context
- Context is prepended to new queries for continuity
- Format: "Previous conversation: [...] Current question: [...]"
- Improves response quality for follow-up questions

### Document Management
- PDF extraction using PyPDF2
- Metadata tracking (pages, words, timestamps)
- Vector store automatic rebuild on changes
- Supports update (re-upload same filename) or remove

### Session Management
- Unique session IDs based on timestamp
- Auto-creation of first session on login
- Most recent session loaded by default
- Independent message histories per session

## Best Practices

1. **Organize Conversations**
   - Create separate sessions for different topics
   - Name sessions descriptively (auto-generated names)
   - Delete old sessions to keep sidebar clean

2. **Document Management**
   - Review documents regularly
   - Remove outdated or duplicate documents
   - Check document details before removal
   - Re-upload to update content

3. **Chat Memory**
   - Take advantage of follow-up questions
   - Reference previous answers naturally
   - Start new session for unrelated topics
   - Context limited to recent exchanges

## Troubleshooting

**Session not switching?**
- Click session name again
- Refresh the page

**Document removal failed?**
- Check if document exists in "Manage" tab
- Ensure you have write permissions
- Try logging out and back in

**Chat memory not working?**
- Verify you're in the same session
- Check that previous messages are visible
- Context only includes last 3 exchanges

## Future Enhancements

Potential improvements for future versions:
- Rename chat sessions
- Export chat history
- Bulk document operations
- Search within documents
- Session sharing between users (admin feature)
- Document categorization/tagging
