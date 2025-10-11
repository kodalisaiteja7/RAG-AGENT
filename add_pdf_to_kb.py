"""
Script to extract PDF content and add it to the knowledge base
"""
import json
import logging
from datetime import datetime
import PyPDF2
from pathlib import Path
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_pdf_content(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    logger.info(f"Extracting content from {pdf_path}...")

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {num_pages} pages")

            content = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    content.append(text)

                if (page_num + 1) % 10 == 0:
                    logger.info(f"Processed {page_num + 1}/{num_pages} pages")

            full_content = "\n\n".join(content)
            logger.info(f"Extracted {len(full_content)} characters")
            return full_content

    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        raise


def add_to_knowledge_base(pdf_path: str, kb_path: str):
    """Add PDF content to existing knowledge base"""

    # Extract PDF content
    content = extract_pdf_content(pdf_path)

    if not content or len(content) < 100:
        raise ValueError("Insufficient content extracted from PDF")

    # Load existing knowledge base
    if Path(kb_path).exists():
        logger.info(f"Loading existing knowledge base from {kb_path}")
        with open(kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    else:
        logger.info("Creating new knowledge base")
        documents = []

    # Create document entry for PDF
    pdf_filename = Path(pdf_path).name

    doc = {
        "title": f"PDF Document: {pdf_filename}",
        "url": f"file:///{pdf_path}",
        "summary": f"Content extracted from {pdf_filename}",
        "content": content,
        "source_type": "pdf_document",
        "date_collected": datetime.now().isoformat(),
        "metadata": {
            "word_count": len(content.split()),
            "filename": pdf_filename
        }
    }

    # Check if PDF already in knowledge base
    existing_idx = None
    for idx, existing_doc in enumerate(documents):
        if existing_doc.get('metadata', {}).get('filename') == pdf_filename:
            existing_idx = idx
            logger.info(f"Found existing entry for {pdf_filename}, will update it")
            break

    if existing_idx is not None:
        documents[existing_idx] = doc
        logger.info("Updated existing PDF entry")
    else:
        documents.append(doc)
        logger.info("Added new PDF entry")

    # Save updated knowledge base
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Saved knowledge base to {kb_path}")
    logger.info(f"✓ Total documents in knowledge base: {len(documents)}")

    return len(documents)


def main():
    """Main execution"""
    pdf_path = "dar.pdf"
    kb_path = config.KB_OUTPUT_PATH

    logger.info("="*70)
    logger.info("Adding PDF to Knowledge Base")
    logger.info("="*70)

    try:
        total_docs = add_to_knowledge_base(pdf_path, kb_path)

        print(f"\n{'='*70}")
        print(f"SUCCESS")
        print(f"{'='*70}")
        print(f"PDF content has been added to the knowledge base")
        print(f"Total documents: {total_docs}")
        print(f"\nNext steps:")
        print(f"1. Rebuild vector database: python vector_store.py")
        print(f"2. Or run: python pipeline.py")

    except Exception as e:
        logger.error(f"Failed to add PDF: {e}")
        raise


if __name__ == "__main__":
    main()
