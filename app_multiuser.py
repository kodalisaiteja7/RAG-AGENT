"""
Multi-User Professional Enterprise RAG System
With authentication, user-specific knowledge bases, and admin panel
"""
import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
from agent2_rag_expert import OneStreamExpert
from multi_user_vector_store import MultiUserVectorStore
from user_manager import get_user_manager
import config

# Initialize database on first run (only if needed)
if 'db_check_done' not in st.session_state:
    try:
        from init_database import init_for_deployment
        import os

        # Only run if KB file doesn't exist (first deployment)
        if not os.path.exists('./onestream_kb.json'):
            with st.spinner("Initializing system for first deployment..."):
                init_for_deployment()

        st.session_state.db_check_done = True
    except Exception as e:
        # Don't show error unless it's critical
        import logging
        logging.warning(f"Initialization check: {e}")
        st.session_state.db_check_done = True

# Page configuration
st.set_page_config(
    page_title="Enterprise RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto"  # Auto-collapse on mobile
)

# Add mobile viewport fix
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #3B82F6;
        --accent-color: #10B981;
        --danger-color: #EF4444;
        --text-color: #1F2937;
        --bg-color: #F9FAFB;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        color: #E0E7FF;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* User badge */
    .user-badge {
        background: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .user-badge .role {
        background: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .user-badge .role.admin {
        background: #F59E0B;
    }

    /* Stat cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    .stat-card h3 {
        color: #6B7280;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-card .value {
        color: #1F2937;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }

    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F9FAFB;
    }

    /* Login form */
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }

    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-header h1 {
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }

    .login-header p {
        color: #6B7280;
    }

    /* ============================================
       RESPONSIVE DESIGN - Mobile & Tablet
       ============================================ */

    /* Tablet styles (768px - 1024px) */
    @media screen and (max-width: 1024px) {
        .main-header {
            padding: 1.5rem;
        }

        .main-header h1 {
            font-size: 2rem;
        }

        .main-header p {
            font-size: 1rem;
        }

        .stat-card .value {
            font-size: 1.5rem;
        }
    }

    /* Mobile styles (max-width: 768px) */
    @media screen and (max-width: 768px) {
        /* Header adjustments */
        .main-header {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
        }

        .main-header h1 {
            font-size: 1.5rem;
            line-height: 1.3;
        }

        .main-header p {
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }

        /* User badge mobile optimization */
        .user-badge {
            padding: 0.5rem 1rem;
            margin-top: 0.75rem;
            font-size: 0.85rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .user-badge .role {
            padding: 0.2rem 0.6rem;
            font-size: 0.75rem;
        }

        /* Stat cards mobile */
        .stat-card {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .stat-card h3 {
            font-size: 0.75rem;
        }

        .stat-card .value {
            font-size: 1.75rem;
        }

        /* ========== ENHANCED MOBILE CHAT FIXES ========== */

        /* Main app container - ensure proper viewport usage */
        .main {
            overflow-x: hidden !important;
            width: 100vw !important;
            max-width: 100% !important;
            background: transparent !important;
        }

        /* Block container - reduce padding for more space */
        .block-container {
            padding: 0.5rem !important;
            padding-bottom: 80px !important; /* Space for sticky input */
            max-width: 100% !important;
            overflow-x: hidden !important;
            background: transparent !important;
        }

        /* Chat messages container - proper scrolling area */
        [data-testid="stVerticalBlock"] {
            overflow-x: hidden !important;
            max-width: 100% !important;
            background: transparent !important;
        }

        /* Remove white backgrounds from app view container */
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background: #f9fafb !important;
        }

        /* Individual chat messages */
        .stChatMessage {
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 8px !important;
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            overflow-x: hidden !important;
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            position: relative !important;
            z-index: 10 !important;
        }

        /* Chat message content wrapper */
        .stChatMessage > div {
            max-width: 100% !important;
            width: 100% !important;
            overflow-x: hidden !important;
            position: relative !important;
            z-index: 11 !important;
        }

        /* Chat message text content */
        .stChatMessage p {
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
            margin-bottom: 0.5rem !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 100% !important;
        }

        /* Chat message content wrapper */
        .stChatMessageContent {
            max-width: 100% !important;
            width: 100% !important;
            overflow-x: hidden !important;
        }

        /* Code blocks in chat - horizontal scroll only for code */
        .stChatMessage pre {
            overflow-x: auto !important;
            overflow-y: hidden !important;
            font-size: 0.85rem !important;
            max-width: 100% !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
        }

        .stChatMessage code {
            font-size: 0.85rem !important;
            word-break: break-all !important;
            white-space: pre-wrap !important;
        }

        /* Chat input container - sticky at bottom */
        .stChatInputContainer {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            padding: 0.75rem !important;
            background: white !important;
            border-top: 1px solid #e5e7eb !important;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1) !important;
            z-index: 10 !important;
            margin: 0 !important;
        }

        /* Chat input field */
        .stChatInput {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
        }

        .stChatInput textarea {
            font-size: 16px !important; /* Prevents zoom on iOS */
            padding: 0.75rem !important;
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box !important;
            border-radius: 8px !important;
        }

        /* Chat message container wrapper */
        [data-testid="stChatMessageContainer"] {
            padding: 0.5rem !important;
            padding-bottom: 90px !important; /* Extra space for fixed input */
            max-width: 100% !important;
            overflow-x: hidden !important;
            background: transparent !important;
            position: relative !important;
            z-index: 1 !important;
        }

        /* Ensure individual chat message wrapper is on top */
        [data-testid="stChatMessageContainer"] > div {
            position: relative !important;
            z-index: 5 !important;
            background: transparent !important;
        }

        /* Buttons mobile - larger touch targets */
        .stButton>button {
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            min-height: 44px;
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Login form mobile */
        .login-container {
            max-width: 100%;
            margin: 1rem;
            padding: 1.5rem;
            border-radius: 12px;
        }

        .login-header h1 {
            font-size: 1.75rem;
        }

        .login-header p {
            font-size: 0.9rem;
        }

        /* Form inputs mobile */
        .stTextInput input,
        .stSelectbox select {
            font-size: 16px !important; /* Prevents zoom on iOS */
            padding: 0.75rem !important;
        }

        /* File uploader mobile */
        .stFileUploader {
            font-size: 0.9rem;
        }

        /* Tabs mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem;
            font-size: 0.9rem;
            white-space: nowrap;
        }

        /* Expander mobile */
        .stExpander {
            border-radius: 8px;
            max-width: 100% !important;
            overflow-x: hidden !important;
        }

        .stExpander summary {
            font-size: 0.9rem;
            padding: 0.75rem;
            word-break: break-word !important;
        }

        .stExpander [data-testid="stExpanderDetails"] {
            max-width: 100% !important;
            overflow-x: hidden !important;
        }

        /* Metrics mobile */
        .stMetric {
            padding: 0.5rem;
        }

        .stMetric label {
            font-size: 0.8rem;
        }

        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.25rem;
        }

        /* Sidebar mobile optimization */
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1rem;
        }

        /* Main content area */
        .main .block-container {
            padding: 0.5rem !important;
            padding-bottom: 90px !important;
            max-width: 100% !important;
        }

        /* Columns mobile - stack vertically */
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }

        /* Divider spacing mobile */
        hr {
            margin: 1rem 0;
        }

        /* Alert boxes mobile */
        .stAlert {
            max-width: 100% !important;
            overflow-x: hidden !important;
        }

        /* Spinner mobile - proper centering and visibility */
        .stSpinner {
            text-align: center;
            padding: 2rem 0;
            width: 100% !important;
        }

        .stSpinner > div {
            margin: 0 auto;
        }

        /* Success/Warning/Error messages mobile */
        .stSuccess, .stWarning, .stError, .stInfo {
            max-width: 100% !important;
            overflow-x: hidden !important;
            word-break: break-word !important;
            font-size: 0.9rem !important;
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
        }

        /* Remove any white overlays that might be covering content */
        .main::before,
        .main::after,
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            display: none !important;
        }

        /* Ensure chat content is visible - specific fixes */
        .stChatMessage {
            min-height: 60px !important;
        }

        /* Simple mobile chat styling - minimal approach */
        .stChatMessage {
            background: #f8f9fa !important;
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 8px !important;
            border: 1px solid #dee2e6 !important;
        }

        .stChatMessage p,
        .stChatMessage div {
            color: #000000 !important;
            font-size: 16px !important;
            line-height: 1.5 !important;
        }

        /* Code blocks visible */
        .stCodeBlock {
            background: #ffffff !important;
            border: 1px solid #000000 !important;
            padding: 10px !important;
        }

        .stCodeBlock code {
            color: #000000 !important;
            font-size: 14px !important;
        }
    }

    /* Small mobile styles (max-width: 480px) */
    @media screen and (max-width: 480px) {
        .main-header h1 {
            font-size: 1.25rem;
        }

        .main-header p {
            font-size: 0.8rem;
        }

        .user-badge {
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
        }

        .user-badge .role {
            font-size: 0.7rem;
        }

        .stat-card .value {
            font-size: 1.5rem;
        }

        .stButton>button {
            font-size: 0.9rem !important;
        }

        .login-container {
            margin: 0.5rem;
            padding: 1rem;
        }

        .login-header h1 {
            font-size: 1.5rem;
        }
    }

    /* Landscape orientation fixes */
    @media screen and (max-height: 600px) and (orientation: landscape) {
        .main-header {
            padding: 0.75rem;
        }

        .main-header h1 {
            font-size: 1.25rem;
        }

        .main-header p {
            display: none; /* Hide subtitle in landscape */
        }

        .stat-card {
            padding: 0.75rem;
        }
    }

    /* Touch device optimizations */
    @media (hover: none) and (pointer: coarse) {
        /* Larger touch targets */
        .stButton>button,
        button {
            min-height: 48px;
            padding: 0.75rem 1.25rem !important;
        }

        /* Better scrolling */
        .stChatMessage {
            -webkit-overflow-scrolling: touch;
        }

        /* Prevent text selection on buttons */
        button {
            -webkit-user-select: none;
            -moz-user-select: none;
            user-select: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "expert" not in st.session_state:
    st.session_state.expert = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

user_manager = get_user_manager()


def get_session_file_path(username: str) -> str:
    """Get the path to user's chat sessions file"""
    return str(Path(f"user_data/{username}/chat_sessions.json"))


def load_chat_sessions(username: str) -> dict:
    """Load user's chat sessions from file"""
    session_file = get_session_file_path(username)
    if Path(session_file).exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_chat_sessions(username: str, sessions: dict):
    """Save user's chat sessions to file"""
    session_file = get_session_file_path(username)
    Path(session_file).parent.mkdir(parents=True, exist_ok=True)
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)


def create_new_session(username: str, session_name: str = None) -> str:
    """Create a new chat session"""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if session_name is None:
        session_name = f"Chat {datetime.now().strftime('%b %d, %H:%M')}"

    if username not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[username] = {}

    st.session_state.chat_sessions[username][session_id] = {
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }

    save_chat_sessions(username, st.session_state.chat_sessions[username])
    return session_id


def get_current_messages() -> list:
    """Get messages from current session"""
    username = st.session_state.username
    session_id = st.session_state.current_session_id

    if (username in st.session_state.chat_sessions and
        session_id in st.session_state.chat_sessions[username]):
        return st.session_state.chat_sessions[username][session_id]["messages"]
    return []


def save_current_messages(messages: list):
    """Save messages to current session"""
    username = st.session_state.username
    session_id = st.session_state.current_session_id

    if username not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[username] = {}

    if session_id not in st.session_state.chat_sessions[username]:
        st.session_state.chat_sessions[username][session_id] = {
            "name": f"Chat {datetime.now().strftime('%b %d, %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "messages": messages
        }
    else:
        st.session_state.chat_sessions[username][session_id]["messages"] = messages

    save_chat_sessions(username, st.session_state.chat_sessions[username])


def login_page():
    """Display login page"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>🤖 Enterprise RAG System</h1>
            <p>AI-Powered Knowledge Management</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            st.markdown("### Sign In")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submit:
                if user_manager.authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_info = user_manager.get_user_info(username)

                    # Load chat sessions
                    st.session_state.chat_sessions[username] = load_chat_sessions(username)

                    # Create initial session if none exist
                    if not st.session_state.chat_sessions[username]:
                        st.session_state.current_session_id = create_new_session(username)
                    else:
                        # Load most recent session
                        sessions = st.session_state.chat_sessions[username]
                        st.session_state.current_session_id = max(sessions.keys())

                    # Initialize vector store for user
                    with st.spinner("Loading your knowledge base..."):
                        try:
                            st.session_state.vector_store = MultiUserVectorStore(username)
                            st.session_state.expert = OneStreamExpert(
                                vector_store=st.session_state.vector_store
                            )
                            st.success("Login successful!")
                            st.rerun()
                        except ValueError as e:
                            st.session_state.authenticated = False
                            st.session_state.username = None
                            st.error(f"⚠️ Configuration Error: {str(e)}")
                            st.info("💡 **Setup Required:** Please configure your XAI_API_KEY in Streamlit Cloud Secrets or environment variables.")
                        except Exception as e:
                            st.session_state.authenticated = False
                            st.session_state.username = None
                            st.error(f"Error initializing system: {str(e)}")
                else:
                    st.error("Invalid username or password")

        st.markdown("---")
        st.info("**Default Admin Credentials:**\n- Username: `admin`\n- Password: `admin123`")


def extract_pdf_content(pdf_file):
    """Extract text content from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        content = []
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text.strip():
                content.append(text)

        full_content = "\n\n".join(content)
        return full_content, num_pages
    except Exception as e:
        return None, str(e)


def add_user_pdf(pdf_file, pdf_name, username):
    """Add PDF to user's knowledge base"""
    content, num_pages = extract_pdf_content(pdf_file)

    if content is None:
        return False, f"Error extracting PDF: {num_pages}"

    if len(content) < 100:
        return False, "Insufficient content extracted from PDF"

    # Load user's KB
    user_kb_path = user_manager.get_user_kb_path(username)
    if Path(user_kb_path).exists():
        with open(user_kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    else:
        documents = []

    # Create document entry
    doc = {
        "title": pdf_name.replace(".pdf", ""),
        "url": f"user_upload://{username}/{pdf_name}",
        "summary": f"User uploaded document: {pdf_name}",
        "content": content,
        "source_type": "user_uploaded",
        "date_collected": datetime.now().isoformat(),
        "metadata": {
            "word_count": len(content.split()),
            "filename": pdf_name,
            "category": "user_upload",
            "num_pages": num_pages,
            "username": username
        }
    }

    # Check if exists and update or add
    existing_idx = None
    for idx, existing_doc in enumerate(documents):
        if existing_doc.get('metadata', {}).get('filename') == pdf_name:
            existing_idx = idx
            break

    if existing_idx is not None:
        documents[existing_idx] = doc
        action = "updated"
    else:
        documents.append(doc)
        action = "added"

    # Save updated user KB
    with open(user_kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    # Rebuild user vector store
    try:
        vector_store = MultiUserVectorStore(username)
        vector_store.embed_user_documents(user_kb_path)

        # Reinitialize expert
        st.session_state.vector_store = vector_store
        st.session_state.expert = OneStreamExpert(vector_store=vector_store)

        return True, f"PDF {action} successfully! Total user documents: {len(documents)}"
    except Exception as e:
        return False, f"Error rebuilding vector store: {str(e)}"


def remove_user_document(username, doc_title):
    """Remove a document from user's knowledge base"""
    user_kb_path = user_manager.get_user_kb_path(username)

    if not Path(user_kb_path).exists():
        return False, "Knowledge base not found"

    # Load user's KB
    with open(user_kb_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    # Find and remove document
    original_count = len(documents)
    documents = [doc for doc in documents if doc.get('title') != doc_title]

    if len(documents) == original_count:
        return False, "Document not found"

    # Save updated KB
    with open(user_kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    # Rebuild vector store
    try:
        vector_store = MultiUserVectorStore(username)
        if documents:  # Only embed if there are documents remaining
            vector_store.embed_user_documents(user_kb_path)
        else:
            # Clear user collection if no documents left
            if vector_store.user_collection:
                vector_store.user_collection.delete(where={"username": username})

        # Reinitialize expert
        st.session_state.vector_store = vector_store
        st.session_state.expert = OneStreamExpert(vector_store=vector_store)

        return True, f"Document removed successfully! Remaining documents: {len(documents)}"
    except Exception as e:
        return False, f"Error rebuilding vector store: {str(e)}"


def get_user_documents(username):
    """Get list of user's uploaded documents"""
    user_kb_path = user_manager.get_user_kb_path(username)

    if not Path(user_kb_path).exists():
        return []

    with open(user_kb_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    return documents


def admin_panel():
    """Admin management panel"""
    st.markdown("## 👤 User Management")

    tab1, tab2 = st.tabs(["Users List", "Add New User"])

    with tab1:
        users = user_manager.list_users()

        for user in users:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                role_badge = "🛡️ Admin" if user['role'] == 'admin' else "👤 User"
                st.markdown(f"**{role_badge} {user['full_name']}**")
                st.caption(f"@{user['username']}")

            with col2:
                st.caption(f"Created: {user['created_at'][:10]}")

            with col3:
                if user['username'] != 'admin':
                    # Count user documents
                    user_kb_path = user_manager.get_user_kb_path(user['username'])
                    if Path(user_kb_path).exists():
                        with open(user_kb_path, 'r', encoding='utf-8') as f:
                            user_docs = json.load(f)
                            st.metric("Documents", len(user_docs))
                    else:
                        st.metric("Documents", 0)

            with col4:
                if user['username'] != 'admin':
                    if st.button("Delete", key=f"del_{user['username']}", type="secondary"):
                        if user_manager.delete_user(user['username']):
                            st.success(f"User {user['username']} deleted")
                            st.rerun()

            st.divider()

    with tab2:
        with st.form("add_user_form"):
            st.markdown("### Create New User")

            new_username = st.text_input("Username")
            new_fullname = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])

            if st.form_submit_button("Create User", type="primary"):
                if new_username and new_password and new_fullname:
                    if user_manager.create_user(new_username, new_password, new_fullname, new_role):
                        st.success(f"User {new_username} created successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill in all fields")


def main_app():
    """Main application after login"""
    username = st.session_state.username
    user_info = st.session_state.user_info
    is_admin = user_manager.is_admin(username)

    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 Enterprise RAG System</h1>
        <p>AI-Powered Knowledge Management Platform</p>
        <div class="user-badge">
            <span>Welcome, <strong>{user_info['full_name']}</strong></span>
            <span class="role {'admin' if is_admin else ''}">{user_info['role'].upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Chat Session Management
        st.markdown("### 💬 Chat Sessions")

        # New session button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_session_id = create_new_session(username)
            st.session_state.current_session_id = new_session_id
            st.rerun()

        # List existing sessions
        if username in st.session_state.chat_sessions:
            sessions = st.session_state.chat_sessions[username]
            if sessions:
                st.markdown("**Your Chats:**")
                for session_id in sorted(sessions.keys(), reverse=True):
                    session = sessions[session_id]
                    is_current = session_id == st.session_state.current_session_id

                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(
                            f"{'📌 ' if is_current else ''}{session['name']}",
                            key=f"session_{session_id}",
                            use_container_width=True,
                            type="secondary" if is_current else "tertiary"
                        ):
                            st.session_state.current_session_id = session_id
                            st.rerun()

                    with col2:
                        if not is_current and st.button("🗑️", key=f"del_session_{session_id}"):
                            del st.session_state.chat_sessions[username][session_id]
                            save_chat_sessions(username, st.session_state.chat_sessions[username])
                            st.rerun()

        st.divider()

        # Knowledge Base Stats
        st.markdown("### 📊 Knowledge Base")
        stats = st.session_state.vector_store.get_stats()

        st.markdown(f"""
        <div class="stat-card">
            <h3>Admin KB</h3>
            <p class="value">{stats['admin_chunks']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card">
            <h3>My Documents</h3>
            <p class="value">{stats['user_chunks']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Document Management
        st.markdown("### 📄 My Documents")

        doc_tab1, doc_tab2 = st.tabs(["Upload", "Manage"])

        with doc_tab1:
            uploaded_file = st.file_uploader(
                "Upload PDF",
                type="pdf",
                help="Add documents to your personal knowledge base"
            )

            if uploaded_file is not None:
                if st.button("Add to KB", type="primary", use_container_width=True):
                    with st.spinner("Processing..."):
                        success, message = add_user_pdf(uploaded_file, uploaded_file.name, username)

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

        with doc_tab2:
            user_docs = get_user_documents(username)
            if user_docs:
                st.caption(f"Total: {len(user_docs)} document(s)")
                for doc in user_docs:
                    with st.expander(f"📄 {doc['title'][:30]}..."):
                        st.caption(f"**Filename:** {doc['metadata']['filename']}")
                        st.caption(f"**Pages:** {doc['metadata']['num_pages']}")
                        st.caption(f"**Words:** {doc['metadata']['word_count']:,}")
                        st.caption(f"**Uploaded:** {doc['date_collected'][:10]}")

                        if st.button(
                            "🗑️ Remove",
                            key=f"remove_{doc['title']}",
                            type="secondary",
                            use_container_width=True
                        ):
                            with st.spinner("Removing..."):
                                success, message = remove_user_document(username, doc['title'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            else:
                st.info("No documents uploaded yet")

        st.divider()

        # Logout
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_session_id = None
            st.rerun()

    # Main content
    if is_admin:
        tab1, tab2 = st.tabs(["💬 Chat", "⚙️ Admin Panel"])

        with tab1:
            chat_interface()

        with tab2:
            admin_panel()
    else:
        chat_interface()


def chat_interface():
    """Chat interface component"""
    # Get messages from current session
    messages = get_current_messages()

    # Display session info
    username = st.session_state.username
    session_id = st.session_state.current_session_id
    if username in st.session_state.chat_sessions and session_id in st.session_state.chat_sessions[username]:
        session = st.session_state.chat_sessions[username][session_id]
        st.caption(f"📝 {session['name']} • Started: {session['created_at'][:16]}")

    # Create a container for chat messages
    chat_container = st.container()

    with chat_container:
        # Display chat history - ALTERNATIVE METHOD WITHOUT st.chat_message
        for idx, message in enumerate(messages):
            role = message["role"]
            content = message.get("content", "")

            # Use regular containers instead of st.chat_message for mobile compatibility
            st.markdown(f"### {'🤖 Assistant' if role == 'assistant' else '👤 You'}")

            # Display content in a simple container with high contrast
            with st.container():
                # Escape HTML in content to prevent rendering issues
                safe_content = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

                st.markdown(f"""
                <div style="background-color: {'#ffffff' if role == 'user' else '#ffffff'};
                                     padding: 20px;
                                     border-radius: 12px;
                                     margin: 15px 0;
                                    border: 3px solid {'#1976d2' if role == 'user' else '#424242'};
                                     box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                           <p style="color: #000000 !important;
                                     font-size: 17px;
                                       line-height: 1.7;
                                    margin: 0;
                                    font-weight: 500;
                                     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                              {safe_content}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Display confidence badge if it's an assistant message
                if role == "assistant" and "confidence" in message:
                    confidence = message["confidence"]
                    if confidence == "high":
                        st.success("✓ High Confidence", icon="✅")
                    elif confidence == "medium":
                        st.warning("⚠ Medium Confidence", icon="⚠️")
                    elif confidence == "low":
                        st.error("⚠ Low Confidence", icon="❌")

                # Display citations if available
                if role == "assistant" and "citations" in message:
                    if message["citations"]:
                        with st.expander("📚 Sources"):
                            for idx, citation in enumerate(message["citations"], 1):
                                is_admin = citation.get('source_type') != 'user_uploaded'
                                badge = "🌐 Admin KB" if is_admin else "📁 My Documents"

                                st.markdown(f"**{idx}. {citation['title']}** {badge}")
                                st.caption(f"Type: {citation['source_type']}")

    # Chat input
    if prompt := st.chat_input("Ask me anything from your knowledge base..."):
        # Add user message immediately
        messages.append({"role": "user", "content": prompt})

        # Build context from previous messages for better continuity
        context_messages = []
        for msg in messages[-6:]:  # Last 3 exchanges (6 messages)
            if msg["role"] == "user":
                context_messages.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                context_messages.append(f"Assistant: {msg['content']}")

        # Add context to current query if there's conversation history
        if len(messages) > 1:
            context_str = "\n".join(context_messages[:-1])  # Exclude current message
            enhanced_prompt = f"Previous conversation:\n{context_str}\n\nCurrent question: {prompt}"
        else:
            enhanced_prompt = prompt

        # Get response
        with st.spinner("🤔 Thinking..."):
            result = st.session_state.expert.answer_question(enhanced_prompt)

            response = result["answer"]
            citations = result["citations"]
            confidence = result["confidence"]

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": response,
            "citations": citations,
            "confidence": confidence
        })

        # Save messages
        save_current_messages(messages)

        # Rerun to display the new messages
        st.rerun()


# Main routing
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
