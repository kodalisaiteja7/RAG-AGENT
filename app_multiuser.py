"""
Multi-User Professional Enterprise RAG System
BRAND NEW UI - Modern Design
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

# Initialize database on first run
if 'db_check_done' not in st.session_state:
    try:
        from init_database import init_for_deployment
        if not os.path.exists('./onestream_kb.json'):
            with st.spinner("Initializing system..."):
                init_for_deployment()
        st.session_state.db_check_done = True
    except Exception as e:
        import logging
        logging.warning(f"Initialization check: {e}")
        st.session_state.db_check_done = True

# Page configuration
st.set_page_config(
    page_title="SmartDoc AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BRAND NEW MODERN CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ========== MODERN COLOR PALETTE ========== */
    :root {
        --primary: #14B8A6;
        --primary-dark: #0D9488;
        --secondary: #8B5CF6;
        --accent: #FF6B6B;
        --success: #10B981;
        --warning: #F59E0B;
        --bg-main: #FFF8F0;
        --bg-card: #FFFFFF;
        --text-dark: #1E293B;
        --text-light: #64748B;
        --border: #E2E8F0;
    }

    /* ========== GLOBAL STYLES ========== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #FFF8F0 0%, #FFE4E6 100%);
    }

    /* ========== MODERN HEADER ========== */
    .modern-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(20, 184, 166, 0.3);
        position: relative;
        overflow: hidden;
    }

    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    .modern-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -1px;
    }

    .modern-header .tagline {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    .user-chip {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: 12px 24px;
        border-radius: 50px;
        margin-top: 1.5rem;
        border: 1px solid rgba(255,255,255,0.3);
    }

    .user-chip .name {
        color: white;
        font-weight: 600;
        font-size: 1rem;
    }

    .user-chip .badge {
        background: var(--accent);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .user-chip .badge.admin {
        background: #FFD700;
        color: #1E293B;
    }

    /* ========== MODERN CHAT BUBBLES ========== */
    .chat-bubble {
        display: inline-block;
        max-width: 85%;
        padding: 18px 24px;
        border-radius: 20px;
        margin: 12px 0;
        font-size: 16px;
        line-height: 1.6;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border-bottom-right-radius: 4px;
        margin-left: auto;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
    }

    .chat-bubble.assistant {
        background: white;
        color: var(--text-dark);
        border-bottom-left-radius: 4px;
        border: 2px solid var(--border);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .chat-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-light);
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .chat-label.user {
        justify-content: flex-end;
    }

    .avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }

    .avatar.user {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    }

    .avatar.assistant {
        background: linear-gradient(135deg, var(--secondary) 0%, var(--accent) 100%);
    }

    /* ========== MODERN CARDS ========== */
    .modern-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--border);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .modern-card .title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-light);
        font-weight: 600;
        margin-bottom: 8px;
    }

    .modern-card .value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-dark);
        line-height: 1;
    }

    .modern-card .icon {
        font-size: 2rem;
        margin-bottom: 12px;
    }

    /* ========== BUTTONS ========== */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
        font-size: 15px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    /* ========== LOGIN PAGE ========== */
    .login-box {
        max-width: 450px;
        margin: 5rem auto;
        padding: 3rem;
        background: white;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    }

    .login-box .logo {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .login-box h1 {
        text-align: center;
        color: var(--text-dark);
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .login-box .subtitle {
        text-align: center;
        color: var(--text-light);
        margin-bottom: 2rem;
        font-size: 1rem;
    }

    /* ========== MOBILE RESPONSIVE ========== */
    @media screen and (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem;
        }

        .modern-header {
            padding: 1.5rem;
        }

        .chat-bubble {
            max-width: 90%;
            padding: 14px 18px;
            font-size: 15px;
        }

        .modern-card .value {
            font-size: 2rem;
        }

        .login-box {
            margin: 2rem 1rem;
            padding: 2rem;
        }

        /* Ensure text visibility */
        .chat-bubble.user,
        .chat-bubble.assistant {
            color: #000000 !important;
        }

        .chat-bubble.user {
            color: #FFFFFF !important;
        }
    }

    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FFF8F0 100%);
        border-right: 2px solid var(--border);
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }

    /* ========== BADGES ========== */
    .confidence-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .confidence-badge.high {
        background: rgba(16, 185, 129, 0.15);
        color: #059669;
    }

    .confidence-badge.medium {
        background: rgba(245, 158, 11, 0.15);
        color: #D97706;
    }

    .confidence-badge.low {
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
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

# Helper functions (keep all existing logic)
def get_session_file_path(username: str) -> str:
    return str(Path(f"user_data/{username}/chat_sessions.json"))

def load_chat_sessions(username: str) -> dict:
    session_file = get_session_file_path(username)
    if Path(session_file).exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_chat_sessions(username: str, sessions: dict):
    session_file = get_session_file_path(username)
    Path(session_file).parent.mkdir(parents=True, exist_ok=True)
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)

def create_new_session(username: str, session_name: str = None) -> str:
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
    username = st.session_state.username
    session_id = st.session_state.current_session_id

    if (username in st.session_state.chat_sessions and
        session_id in st.session_state.chat_sessions[username]):
        return st.session_state.chat_sessions[username][session_id]["messages"]
    return []

def save_current_messages(messages: list):
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

def extract_pdf_content(pdf_file):
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
    content, num_pages = extract_pdf_content(pdf_file)

    if content is None:
        return False, f"Error extracting PDF: {num_pages}"

    if len(content) < 100:
        return False, "Insufficient content extracted from PDF"

    user_kb_path = user_manager.get_user_kb_path(username)
    if Path(user_kb_path).exists():
        with open(user_kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    else:
        documents = []

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

    with open(user_kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    try:
        vector_store = MultiUserVectorStore(username)
        vector_store.embed_user_documents(user_kb_path)

        st.session_state.vector_store = vector_store
        st.session_state.expert = OneStreamExpert(vector_store=vector_store)

        return True, f"PDF {action} successfully! Total user documents: {len(documents)}"
    except Exception as e:
        return False, f"Error rebuilding vector store: {str(e)}"

def remove_user_document(username, doc_title):
    user_kb_path = user_manager.get_user_kb_path(username)

    if not Path(user_kb_path).exists():
        return False, "Knowledge base not found"

    with open(user_kb_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    original_count = len(documents)
    documents = [doc for doc in documents if doc.get('title') != doc_title]

    if len(documents) == original_count:
        return False, "Document not found"

    with open(user_kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    try:
        vector_store = MultiUserVectorStore(username)
        if documents:
            vector_store.embed_user_documents(user_kb_path)
        else:
            if vector_store.user_collection:
                vector_store.user_collection.delete(where={"username": username})

        st.session_state.vector_store = vector_store
        st.session_state.expert = OneStreamExpert(vector_store=vector_store)

        return True, f"Document removed successfully! Remaining documents: {len(documents)}"
    except Exception as e:
        return False, f"Error rebuilding vector store: {str(e)}"

def get_user_documents(username):
    user_kb_path = user_manager.get_user_kb_path(username)

    if not Path(user_kb_path).exists():
        return []

    with open(user_kb_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    return documents

def admin_panel():
    st.markdown("## 👥 User Management")

    tab1, tab2 = st.tabs(["Users List", "Add New User"])

    with tab1:
        users = user_manager.list_users()

        for user in users:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    role_badge = "🛡️ Admin" if user['role'] == 'admin' else "👤 User"
                    st.markdown(f"**{role_badge} {user['full_name']}**")
                    st.caption(f"@{user['username']}")

                with col2:
                    st.caption(f"Created: {user['created_at'][:10]}")

                with col3:
                    if user['username'] != 'admin':
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

def login_page():
    st.markdown("""
    <div class="login-box">
        <div class="logo">✨</div>
        <h1>SmartDoc AI</h1>
        <p class="subtitle">Intelligent Knowledge Management System</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submit:
                if user_manager.authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_info = user_manager.get_user_info(username)

                    st.session_state.chat_sessions[username] = load_chat_sessions(username)

                    if not st.session_state.chat_sessions[username]:
                        st.session_state.current_session_id = create_new_session(username)
                    else:
                        sessions = st.session_state.chat_sessions[username]
                        st.session_state.current_session_id = max(sessions.keys())

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
                            st.info("💡 **Setup Required:** Please configure your XAI_API_KEY")
                        except Exception as e:
                            st.session_state.authenticated = False
                            st.session_state.username = None
                            st.error(f"Error initializing system: {str(e)}")
                else:
                    st.error("Invalid username or password")

        st.markdown("---")
        st.info("**Default Admin Credentials:**\n- Username: `admin`\n- Password: `admin123`")

def chat_interface():
    messages = get_current_messages()

    username = st.session_state.username
    session_id = st.session_state.current_session_id
    if username in st.session_state.chat_sessions and session_id in st.session_state.chat_sessions[username]:
        session = st.session_state.chat_sessions[username][session_id]
        st.caption(f"📝 {session['name']} • Started: {session['created_at'][:16]}")

    # Display chat messages with new bubble design
    for message in messages:
        role = message["role"]
        content = message.get("content", "")

        # Label with avatar
        avatar_emoji = "👤" if role == "user" else "🤖"
        label_text = "You" if role == "user" else "Assistant"

        col1, col2 = st.columns([1, 20])
        with (col2 if role == "user" else col1):
            st.markdown(f"""
            <div class="chat-label {role}">
                <span class="avatar {role}">{avatar_emoji}</span>
                <span>{label_text}</span>
            </div>
            """, unsafe_allow_html=True)

        # Chat bubble
        safe_content = content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

        col1, col2 = st.columns([1, 20])
        with (col2 if role == "user" else col1):
            st.markdown(f"""
            <div class="chat-bubble {role}">
                {safe_content}
            </div>
            """, unsafe_allow_html=True)

        # Confidence badge
        if role == "assistant" and "confidence" in message:
            confidence = message["confidence"]
            st.markdown(f"""
            <div class="confidence-badge {confidence}">
                {confidence} confidence
            </div>
            """, unsafe_allow_html=True)

        # Citations
        if role == "assistant" and "citations" in message:
            if message["citations"]:
                with st.expander("📚 Sources"):
                    for idx, citation in enumerate(message["citations"], 1):
                        is_admin = citation.get('source_type') != 'user_uploaded'
                        badge = "🌐 Admin KB" if is_admin else "📁 My Documents"
                        st.markdown(f"**{idx}. {citation['title']}** {badge}")
                        st.caption(f"Type: {citation['source_type']}")

        st.markdown("<br>", unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        messages.append({"role": "user", "content": prompt})

        context_messages = []
        for msg in messages[-6:]:
            if msg["role"] == "user":
                context_messages.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                context_messages.append(f"Assistant: {msg['content']}")

        if len(messages) > 1:
            context_str = "\n".join(context_messages[:-1])
            enhanced_prompt = f"Previous conversation:\n{context_str}\n\nCurrent question: {prompt}"
        else:
            enhanced_prompt = prompt

        with st.spinner("🤔 Thinking..."):
            result = st.session_state.expert.answer_question(enhanced_prompt)

            response = result["answer"]
            citations = result["citations"]
            confidence = result["confidence"]

        messages.append({
            "role": "assistant",
            "content": response,
            "citations": citations,
            "confidence": confidence
        })

        save_current_messages(messages)
        st.rerun()

def main_app():
    username = st.session_state.username
    user_info = st.session_state.user_info
    is_admin = user_manager.is_admin(username)

    # Modern header
    st.markdown(f"""
    <div class="modern-header">
        <h1>✨ SmartDoc AI</h1>
        <p class="tagline">Your Intelligent Knowledge Assistant</p>
        <div class="user-chip">
            <span class="name">Welcome, {user_info['full_name']}</span>
            <span class="badge {'admin' if is_admin else ''}">{user_info['role']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 💬 Chat Sessions")

        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_session_id = create_new_session(username)
            st.session_state.current_session_id = new_session_id
            st.rerun()

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

        st.markdown("### 📊 Knowledge Base")
        stats = st.session_state.vector_store.get_stats()

        st.markdown(f"""
        <div class="modern-card">
            <div class="icon">🌐</div>
            <div class="title">Admin KB</div>
            <div class="value">{stats['admin_chunks']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="modern-card">
            <div class="icon">📁</div>
            <div class="title">My Documents</div>
            <div class="value">{stats['user_chunks']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

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

# Main routing
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
