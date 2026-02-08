"""ArXiv source adapter for SynapseScanner."""
import xml.etree.ElementTree as ET
from typing import List
from . import Paper, BaseSource, register_source


class ArXivSource(BaseSource):
    """ArXiv paper source using the official API."""
    
    API_URL = "https://export.arxiv.org/api/query"
    
    def __init__(self, name: str = "arxiv"):
        super().__init__(name)
        self.ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search ArXiv for papers matching the query."""
        papers = []
        
        # Build search query
        search_query = f"all:{query}" if query else "all"
        
        try:
            session = self._requests_session()
            resp = session.get(
                self.API_URL,
                params={
                    "search_query": search_query,
                    "start": 0,
                    "max_results": limit,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                },
                timeout=30
            )
            resp.raise_for_status()
            
            root = ET.fromstring(resp.text)
            
            for entry in root.findall("atom:entry", self.ns):
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)
                    
        except Exception as e:
            # Log error but return what we have
            pass
        
        return papers
    
    def _parse_entry(self, entry) -> Paper:
        """Parse an ArXiv atom entry into a Paper."""
        # Get title
        title_elem = entry.find("atom:title", self.ns)
        title = title_elem.text.strip() if title_elem is not None else "Unknown"
        
        # Get abstract/summary
        summary_elem = entry.find("atom:summary", self.ns)
        abstract = summary_elem.text.strip() if summary_elem is not None else ""
        
        # Get URL and ID
        id_elem = entry.find("atom:id", self.ns)
        url = id_elem.text.strip() if id_elem is not None else ""
        
        # Extract arXiv ID from URL
        arxiv_id = url.split("/")[-1] if url else ""
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.split("v")[0]
        
        # Get PDF URL
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else ""
        
        # Get published date
        published_elem = entry.find("atom:published", self.ns)
        published = published_elem.text.strip() if published_elem is not None else ""
        
        # Get authors
        authors = []
        for author in entry.findall("atom:author", self.ns):
            name_elem = author.find("atom:name", self.ns)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        
        # Get categories/keywords
        keywords = []
        for category in entry.findall("atom:category", self.ns):
            term = category.get("term", "")
            if term:
                keywords.append(term.lower())
        
        # Extract additional keywords from title and abstract
        text_keywords = self._extract_keywords(title + " " + abstract)
        keywords.extend([k for k in text_keywords if k not in keywords])
        
        return Paper(
            id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            pdf_url=pdf_url,
            published=published,
            source="arxiv",
            citations=0,  # ArXiv doesn't provide citation counts
            keywords=keywords[:20]  # Limit keywords
        )
    
    def fetch_references(self, paper: Paper) -> List[Paper]:
        """ArXiv doesn't provide citation/reference data via API."""
        return []


# Register the source
register_source("arxiv", ArXivSource)
