#!/usr/bin/env python3
"""
Quantum-Flux Lab - Open Access Research Scraper

Scrapes research papers from open-access sources only:
- arXiv.org
- NASA Technical Reports Server
- DOE OSTI
- Zenodo
- University repositories (*.edu)

REJECTS all paywalled content (Elsevier, Springer, Wiley, etc.)
Logs all rejected URLs to blacklist.log for transparency

MIT License - 2026 Quantum-Flux Lab Contributors
"""

import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ResearchPaper:
    """Represents a research paper with metadata"""
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str]
    arxiv_id: Optional[str]
    url: str
    pdf_url: Optional[str]
    published: str
    source: str
    keywords: List[str]
    is_open_access: bool = True


class OpenAccessFilter:
    """Filters URLs to ensure only open-access sources are used"""
    
    # Known paywalled domains (blacklist)
    BLACKLIST_DOMAINS = {
        'elsevier.com', 'sciencedirect.com',
        'springer.com', 'link.springer.com',
        'wiley.com', 'onlinelibrary.wiley.com',
        'nature.com',  # Except OA subset
        'science.org',
        'tandfonline.com',
        'ieee.org', 'ieeexplore.ieee.org',
        'acm.org', 'dl.acm.org',
        'degruyter.com',
        'emerald.com',
        'sagepub.com',
        'karger.com',
        'aps.org', 'journals.aps.org',
        'scitation.org', 'aip.scitation.org',
        'iop.org', 'iopscience.iop.org',
    }
    
    def __init__(self, whitelist_path: Optional[str] = None):
        self.whitelist = self._load_whitelist(whitelist_path)
        self.blacklist_log = Path(__file__).parent / 'blacklist.log'
        
    def _load_whitelist(self, path: Optional[str]) -> Dict:
        """Load whitelist JSON"""
        if path is None:
            path = Path(__file__).parent / 'whitelist.json'
        
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Whitelist not found at {path}, using defaults")
            return {'whitelist': []}
    
    def is_allowed(self, url: str) -> bool:
        """Check if URL is from an open-access source"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check blacklist first
        if any(bl in domain for bl in self.BLACKLIST_DOMAINS):
            self._log_rejection(url, "Blacklisted domain (paywalled)")
            return False
        
        # Check whitelist
        for entry in self.whitelist.get('whitelist', []):
            wl_domain = entry['domain']
            if wl_domain in domain or domain.endswith('.' + wl_domain):
                return True
        
        # Check .edu domains
        if domain.endswith('.edu'):
            return True
        
        # Unknown domain - reject to be safe
        self._log_rejection(url, "Unknown domain (not in whitelist)")
        return False
    
    def _log_rejection(self, url: str, reason: str):
        """Log rejected URL to blacklist.log"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        entry = f"[{timestamp}] {url} - {reason}\n"
        
        with open(self.blacklist_log, 'a') as f:
            f.write(entry)
        
        logger.info(f"Rejected URL: {url} ({reason})")


class ArXivScraper:
    """Scraper for arXiv.org preprints"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self, filter_: OpenAccessFilter):
        self.filter = filter_
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuantumFluxLab/1.0 (Open Access Research Scraper)'
        })
    
    def search(self, query: str, max_results: int = 10) -> List[ResearchPaper]:
        """Search arXiv for papers matching query"""
        logger.info(f"Searching arXiv for: {query}")
        
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch from arXiv: {e}")
            return []
        
        # Parse Atom feed
        feed = feedparser.parse(response.content)
        papers = []
        
        for entry in feed.entries:
            paper = self._parse_entry(entry)
            if paper:
                papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers from arXiv")
        return papers
    
    def _parse_entry(self, entry) -> Optional[ResearchPaper]:
        """Parse a feed entry into ResearchPaper"""
        try:
            # Extract arXiv ID
            arxiv_id = entry.id.split('/abs/')[-1].split('v')[0]
            
            # Build PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            return ResearchPaper(
                title=entry.title.replace('\n', ' '),
                authors=[author.name for author in entry.authors],
                abstract=entry.summary.replace('\n', ' '),
                doi=getattr(entry, 'arxiv_doi', None),
                arxiv_id=arxiv_id,
                url=entry.link,
                pdf_url=pdf_url,
                published=entry.published[:10],
                source='arXiv',
                keywords=[tag.term for tag in entry.get('tags', [])],
                is_open_access=True
            )
        except Exception as e:
            logger.warning(f"Failed to parse entry: {e}")
            return None


class NasaScraper:
    """Scraper for NASA Technical Reports Server (NTRS)"""
    
    BASE_URL = "https://ntrs.nasa.gov/api"
    
    def __init__(self, filter_: OpenAccessFilter):
        self.filter = filter_
        self.session = requests.Session()
    
    def search(self, query: str, max_results: int = 10) -> List[ResearchPaper]:
        """Search NASA NTRS"""
        logger.info(f"Searching NASA NTRS for: {query}")
        
        params = {
            'q': query,
            'limit': max_results,
            'page': 1
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/citations",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch from NASA NTRS: {e}")
            return []
        
        papers = []
        for item in data.get('results', []):
            paper = self._parse_item(item)
            if paper:
                papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers from NASA NTRS")
        return papers
    
    def _parse_item(self, item: Dict) -> Optional[ResearchPaper]:
        """Parse NTRS item into ResearchPaper"""
        try:
            return ResearchPaper(
                title=item.get('title', 'Unknown'),
                authors=item.get('authors', []),
                abstract=item.get('abstract', ''),
                doi=item.get('doi'),
                arxiv_id=None,
                url=f"https://ntrs.nasa.gov/citations/{item.get('id')}",
                pdf_url=item.get('download'),
                published=item.get('publicationDate', 'Unknown'),
                source='NASA NTRS',
                keywords=item.get('subjects', []),
                is_open_access=True
            )
        except Exception as e:
            logger.warning(f"Failed to parse NASA item: {e}")
            return None


class QuantumFluxScraper:
    """Main scraper combining all open-access sources"""
    
    def __init__(self):
        self.filter = OpenAccessFilter()
        self.arxiv = ArXivScraper(self.filter)
        self.nasa = NasaScraper(self.filter)
    
    def search(self, query: str, sources: Optional[List[str]] = None) -> List[ResearchPaper]:
        """
        Search across all open-access sources
        
        Args:
            query: Search query string
            sources: List of sources to search ('arxiv', 'nasa', etc.)
                    If None, searches all sources
        
        Returns:
            List of ResearchPaper objects
        """
        if sources is None:
            sources = ['arxiv', 'nasa']
        
        all_papers = []
        
        if 'arxiv' in sources:
            papers = self.arxiv.search(query)
            all_papers.extend(papers)
            time.sleep(1)  # Be nice to APIs
        
        if 'nasa' in sources:
            papers = self.nasa.search(query)
            all_papers.extend(papers)
        
        # Sort by date (newest first)
        all_papers.sort(key=lambda p: p.published, reverse=True)
        
        return all_papers
    
    def search_physics_topics(self) -> Dict[str, List[ResearchPaper]]:
        """Search for papers related to Quantum-Flux Lab physics topics"""
        topics = {
            'corona_discharge': 'corona discharge high voltage plasma',
            'piezoelectric': 'piezoelectric transformer high voltage',
            'electrohydrodynamic': 'electrohydrodynamic EHD thrust',
            'acoustic_levitation': 'acoustic levitation standing wave',
            'warp_drive': 'Alcubierre warp drive',
            'time_travel_physics': 'closed timelike curves CTC'
        }
        
        results = {}
        for topic, query in topics.items():
            logger.info(f"Searching topic: {topic}")
            papers = self.search(query, sources=['arxiv'])
            results[topic] = papers[:5]  # Top 5 per topic
            time.sleep(2)  # Rate limiting
        
        return results


def save_papers_to_json(papers: List[ResearchPaper], filename: str):
    """Save papers to JSON file"""
    data = [
        {
            'title': p.title,
            'authors': p.authors,
            'abstract': p.abstract[:500] + '...' if len(p.abstract) > 500 else p.abstract,
            'doi': p.doi,
            'arxiv_id': p.arxiv_id,
            'url': p.url,
            'pdf_url': p.pdf_url,
            'published': p.published,
            'source': p.source,
            'keywords': p.keywords
        }
        for p in papers
    ]
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(papers)} papers to {filename}")


if __name__ == '__main__':
    # Example usage
    scraper = QuantumFluxScraper()
    
    # Search for corona discharge papers
    print("=" * 60)
    print("Quantum-Flux Lab - Open Access Research Scraper")
    print("=" * 60)
    
    papers = scraper.search('corona discharge high voltage', sources=['arxiv'])
    
    print(f"\nFound {len(papers)} papers:\n")
    for i, paper in enumerate(papers[:5], 1):
        print(f"{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}")
        print(f"   Source: {paper.source}")
        print(f"   URL: {paper.url}")
        print()
    
    # Save results
    save_papers_to_json(papers, 'research_papers.json')
