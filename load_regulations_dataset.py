"""
Batch load all PDF files from Regulations Dataset into the knowledge base
"""
import json
import logging
from datetime import datetime
from pathlib import Path
import PyPDF2
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_pdf_content(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    logger.info(f"Extracting content from {Path(pdf_path).name}...")

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            content = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    content.append(text)

                if (page_num + 1) % 50 == 0:
                    logger.info(f"  Processed {page_num + 1}/{num_pages} pages")

            full_content = "\n\n".join(content)
            logger.info(f"  Extracted {len(full_content)} characters from {num_pages} pages")
            return full_content

    except Exception as e:
        logger.error(f"Error extracting PDF {pdf_path}: {e}")
        return None


def load_regulations_dataset(dataset_dir: str, kb_path: str):
    """
    Load all PDF files from the Regulations Dataset directory into knowledge base
    """
    dataset_path = Path(dataset_dir)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    # Get all PDF files
    pdf_files = sorted(dataset_path.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(f"No PDF files found in {dataset_dir}")

    logger.info(f"Found {len(pdf_files)} PDF files in {dataset_dir}")

    # Load existing knowledge base or create new one
    if Path(kb_path).exists():
        logger.info(f"Loading existing knowledge base from {kb_path}")
        with open(kb_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        logger.info(f"Existing knowledge base has {len(documents)} documents")
    else:
        logger.info("Creating new knowledge base")
        documents = []

    # Track statistics
    added_count = 0
    updated_count = 0
    skipped_count = 0
    failed_count = 0

    # Process each PDF
    for idx, pdf_path in enumerate(pdf_files, 1):
        pdf_filename = pdf_path.name

        logger.info(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_filename}")

        # Extract content
        content = extract_pdf_content(str(pdf_path))

        if not content or len(content) < 100:
            logger.warning(f"  Insufficient content extracted, skipping")
            failed_count += 1
            continue

        # Create document entry
        doc = {
            "title": pdf_filename.replace(".pdf", ""),
            "url": f"file:///{pdf_path}",
            "summary": f"Regulatory document: {pdf_filename}",
            "content": content,
            "source_type": "regulation_document",
            "date_collected": datetime.now().isoformat(),
            "metadata": {
                "word_count": len(content.split()),
                "filename": pdf_filename,
                "category": "regulations"
            }
        }

        # Check if PDF already in knowledge base
        existing_idx = None
        for doc_idx, existing_doc in enumerate(documents):
            if existing_doc.get('metadata', {}).get('filename') == pdf_filename:
                existing_idx = doc_idx
                break

        if existing_idx is not None:
            documents[existing_idx] = doc
            updated_count += 1
            logger.info(f"  Updated existing entry")
        else:
            documents.append(doc)
            added_count += 1
            logger.info(f"  Added new entry")

    # Save updated knowledge base
    logger.info(f"\nSaving knowledge base to {kb_path}...")
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    logger.info("="*70)
    logger.info("BATCH LOAD COMPLETE")
    logger.info("="*70)
    logger.info(f"Total documents in knowledge base: {len(documents)}")
    logger.info(f"  Added: {added_count}")
    logger.info(f"  Updated: {updated_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info("="*70)

    return {
        "total_documents": len(documents),
        "added": added_count,
        "updated": updated_count,
        "failed": failed_count
    }


def main():
    """Main execution"""
    dataset_dir = "Regulations Dataset"
    kb_path = config.KB_OUTPUT_PATH

    logger.info("="*70)
    logger.info("Loading Regulations Dataset into Knowledge Base")
    logger.info("="*70)

    try:
        stats = load_regulations_dataset(dataset_dir, kb_path)

        print(f"\n{'='*70}")
        print(f"SUCCESS")
        print(f"{'='*70}")
        print(f"Regulations Dataset has been loaded into the knowledge base")
        print(f"Total documents: {stats['total_documents']}")
        print(f"  New documents added: {stats['added']}")
        print(f"  Documents updated: {stats['updated']}")
        print(f"  Documents failed: {stats['failed']}")
        print(f"\nNext steps:")
        print(f"1. Rebuild vector database: python vector_store.py")
        print(f"2. Or run: python pipeline.py")

    except Exception as e:
        logger.error(f"Failed to load regulations dataset: {e}")
        raise


if __name__ == "__main__":
    main()
