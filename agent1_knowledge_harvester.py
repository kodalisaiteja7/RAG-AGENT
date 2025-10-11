"""
Agent 1: OneStream Knowledge Harvester
Crawls and collects OneStream-related content from the web
"""
import json
import logging
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import trafilatura
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDocument:
    """Structured knowledge document"""
    title: str
    url: str
    summary: str
    content: str
    source_type: str
    date_collected: str
    metadata: Dict


class KnowledgeHarvester:
    """Agent 1: Collects and preprocesses OneStream knowledge"""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.visited_urls = set()
        self.documents = []

    def is_relevant_page(self, url: str, content: str) -> bool:
        """Check if page is relevant using GPT-4o"""
        try:
            # Quick heuristic first
            marketing_keywords = ['pricing', 'contact-us', 'demo-request', 'privacy-policy']
            if any(keyword in url.lower() for keyword in marketing_keywords):
                return False

            # For detailed check, use GPT-4o
            prompt = f"""Is this content relevant for a OneStream technical knowledge base?
            It should contain technical information, tutorials, guides, or documentation.
            Exclude marketing pages, generic company info, or contact pages.

            URL: {url}
            Content preview: {content[:500]}

            Answer with just YES or NO."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0
            )

            return "YES" in response.choices[0].message.content.upper()

        except Exception as e:
            logger.error(f"Error checking relevance: {e}")
            return True  # Default to including if check fails

    def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from URL using trafilatura"""
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            # Use trafilatura for content extraction
            content = trafilatura.extract(response.text, include_comments=False)
            return content

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def summarize_content(self, content: str, url: str) -> str:
        """Summarize content using GPT-4o"""
        try:
            prompt = f"""Summarize this OneStream-related content in 2-3 sentences.
            Focus on the key technical information, concepts, or instructions.

            Content:
            {content[:3000]}
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return content[:200] + "..."

    def extract_title(self, html: str, url: str) -> str:
        """Extract page title"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            if title:
                return title.get_text().strip()

            # Fallback to h1
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()

            return urlparse(url).path

        except Exception as e:
            return url

    def crawl_url(self, url: str, max_depth: int = 2, current_depth: int = 0) -> List[str]:
        """Crawl URL and return list of linked pages"""
        if current_depth >= max_depth or url in self.visited_urls:
            return []

        self.visited_urls.add(url)
        linked_urls = []

        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            base_domain = urlparse(url).netloc

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)

                # Only follow links within the same domain
                if urlparse(full_url).netloc == base_domain:
                    if full_url not in self.visited_urls:
                        linked_urls.append(full_url)

            return linked_urls[:config.MAX_PAGES_PER_DOMAIN]

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return []

    def process_url(self, url: str) -> Optional[KnowledgeDocument]:
        """Process a single URL and create knowledge document"""
        try:
            logger.info(f"Processing: {url}")

            # Get raw HTML for title extraction
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            html = response.text

            # Extract main content
            content = self.extract_content(url)
            if not content or len(content) < 100:
                logger.info(f"Insufficient content in {url}")
                return None

            # Check relevance
            if not self.is_relevant_page(url, content):
                logger.info(f"Irrelevant page: {url}")
                return None

            # Extract metadata
            title = self.extract_title(html, url)
            summary = self.summarize_content(content, url)

            # Determine source type
            source_type = "documentation"
            if "community" in url:
                source_type = "community"
            elif "blog" in url:
                source_type = "blog"

            doc = KnowledgeDocument(
                title=title,
                url=url,
                summary=summary,
                content=content,
                source_type=source_type,
                date_collected=datetime.now().isoformat(),
                metadata={"word_count": len(content.split())}
            )

            return doc

        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None

    def harvest(self, urls: List[str]) -> List[KnowledgeDocument]:
        """Main harvesting method"""
        logger.info("Starting knowledge harvesting...")

        all_urls = set(urls)

        # Crawl to discover more pages
        for base_url in urls:
            logger.info(f"Crawling {base_url}...")
            discovered = self.crawl_url(base_url, max_depth=2)
            all_urls.update(discovered)
            time.sleep(config.CRAWL_DELAY)

        logger.info(f"Found {len(all_urls)} URLs to process")

        # Process each URL
        for url in tqdm(list(all_urls)[:config.MAX_PAGES_PER_DOMAIN]):
            doc = self.process_url(url)
            if doc:
                self.documents.append(doc)
            time.sleep(config.CRAWL_DELAY)

        logger.info(f"Harvested {len(self.documents)} documents")
        return self.documents

    def save_knowledge_base(self, output_path: str):
        """Save knowledge base to JSON"""
        data = [asdict(doc) for doc in self.documents]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved knowledge base to {output_path}")


def main():
    """Run Knowledge Harvester"""
    harvester = KnowledgeHarvester()

    # Harvest from configured URLs
    documents = harvester.harvest(config.ONESTREAM_URLS)

    # Save to file
    harvester.save_knowledge_base(config.KB_OUTPUT_PATH)

    print(f"\n✓ Harvested {len(documents)} documents")
    print(f"✓ Saved to {config.KB_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
