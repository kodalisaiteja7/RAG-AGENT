"""
Streamlit UI for Regulatory Agent RAG System
Provides chat interface and PDF document upload functionality
"""
import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
from agent2_rag_expert import OneStreamExpert
from vector_store import VectorStore
import config

# Page configuration
st.set_page_config(
    page_title="Regulatory Agent RAG",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "expert" not in st.session_state:
    with st.spinner("Loading RAG system..."):
        st.session_state.expert = OneStreamExpert()

if "upload_success" not in st.session_state:
    st.session_state.upload_success = None


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


def add_pdf_to_knowledge_base(pdf_file, pdf_name):
    """Add uploaded PDF to knowledge base and rebuild vector store"""
    # Extract content
    content, num_pages = extract_pdf_content(pdf_file)

    if content is None:
        return False, f"Error extracting PDF: {num_pages}"

    if len(content) < 100:
        return False, "Insufficient content extracted from PDF"

    # Load existing knowledge base
    kb_path = config.KB_OUTPUT_PATH
    if Path(kb_path).exists():
        with open(kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    else:
        documents = []

    # Create document entry
    doc = {
        "title": pdf_name.replace(".pdf", ""),
        "url": f"uploaded://{pdf_name}",
        "summary": f"User uploaded document: {pdf_name}",
        "content": content,
        "source_type": "user_uploaded",
        "date_collected": datetime.now().isoformat(),
        "metadata": {
            "word_count": len(content.split()),
            "filename": pdf_name,
            "category": "user_upload",
            "num_pages": num_pages
        }
    }

    # Check if already exists and update or add
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

    # Save updated knowledge base
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    # Rebuild vector store
    try:
        vector_store = VectorStore()
        vector_store.embed_documents(kb_path)

        # Reinitialize expert with updated vector store
        st.session_state.expert = OneStreamExpert(vector_store=vector_store)

        return True, f"PDF {action} successfully! Total documents: {len(documents)}"
    except Exception as e:
        return False, f"Error rebuilding vector store: {str(e)}"


# Main UI Layout
st.title("📚 Regulatory Agent RAG")
st.markdown("Ask questions about regulations and federal appropriations law")

# Sidebar for PDF upload
with st.sidebar:
    st.header("📄 Add Documents")
    st.markdown("Upload PDF documents to add to the knowledge base")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload regulatory documents to expand the knowledge base"
    )

    if uploaded_file is not None:
        if st.button("Add to Knowledge Base", type="primary"):
            with st.spinner("Processing PDF and rebuilding vector database..."):
                success, message = add_pdf_to_knowledge_base(
                    uploaded_file,
                    uploaded_file.name
                )

                if success:
                    st.success(message)
                    st.session_state.upload_success = True
                else:
                    st.error(message)
                    st.session_state.upload_success = False

    st.divider()

    # Knowledge base stats
    st.header("📊 Knowledge Base Stats")
    try:
        if Path(config.KB_OUTPUT_PATH).exists():
            with open(config.KB_OUTPUT_PATH, 'r', encoding='utf-8') as f:
                documents = json.load(f)
                st.metric("Total Documents", len(documents))

                # Count by source type
                source_types = {}
                for doc in documents:
                    src_type = doc.get('source_type', 'unknown')
                    source_types[src_type] = source_types.get(src_type, 0) + 1

                st.write("**By Source:**")
                for src_type, count in source_types.items():
                    st.write(f"- {src_type}: {count}")

        # Vector DB stats
        stats = st.session_state.expert.vector_store.get_stats()
        st.metric("Vector Chunks", stats['total_chunks'])

    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")

    st.divider()

    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
chat_container = st.container()

with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display sources if available
            if message["role"] == "assistant" and "citations" in message:
                if message["citations"]:
                    with st.expander("📚 Sources"):
                        for idx, citation in enumerate(message["citations"], 1):
                            st.markdown(f"**{idx}. {citation['title']}**")
                            st.markdown(f"   - URL: {citation['url']}")
                            st.markdown(f"   - Type: {citation['source_type']}")

# Chat input
if prompt := st.chat_input("Ask a question about regulations..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from RAG system
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.expert.answer_question(prompt)

            response = result["answer"]
            citations = result["citations"]
            confidence = result["confidence"]

            # Display response
            st.markdown(response)

            # Display confidence badge
            if confidence == "high":
                st.success(f"Confidence: {confidence}")
            elif confidence == "medium":
                st.warning(f"Confidence: {confidence}")
            else:
                st.error(f"Confidence: {confidence}")

            # Display sources
            if citations:
                with st.expander("📚 Sources"):
                    for idx, citation in enumerate(citations, 1):
                        st.markdown(f"**{idx}. {citation['title']}**")
                        st.markdown(f"   - URL: {citation['url']}")
                        st.markdown(f"   - Type: {citation['source_type']}")

    # Add assistant response to chat
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "citations": citations,
        "confidence": confidence
    })

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Regulatory Agent RAG System | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
