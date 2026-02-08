"""Semantic Scholar source adapter for SynapseScanner."""
import time
from typing import List, Dict, Any
from . import Paper, BaseSource, register_source


class SemanticScholarSource(BaseSource):
    """Semantic Scholar paper source using the public API."""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, name: str = "semantic_scholar"):
        super().__init__(name)
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search Semantic Scholar for papers matching the query."""
        papers = []
        
        try:
            session = self._requests_session()
            
            # Search endpoint
            url = f"{self.BASE_URL}/paper/search"
            params = {
                "query": query,
                "fields": "paperId,title,authors,year,abstract,url,openAccessPdf,citationCount,referenceCount",
                "limit": limit
            }
            
            resp = session.get(url, params=params, timeout=30)
            
            # Rate limiting - be nice to the API
            time.sleep(0.5)
            
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    paper = self._parse_paper(item)
                    if paper:
                        papers.append(paper)
            elif resp.status_code == 429:
                # Rate limited
                pass
                    
        except Exception:
            pass
        
        return papers
    
    def _parse_paper(self, data: Dict[str, Any]) -> Paper:
        """Parse Semantic Scholar data into a Paper."""
        paper_id = data.get("paperId", "")
        title = data.get("title", "Unknown")
        abstract = data.get("abstract", "") or ""
        
        # Get URL - prefer Semantic Scholar URL
        url = data.get("url", "")
        if not url and paper_id:
            url = f"https://www.semanticscholar.org/paper/{paper_id}"
        
        # Get PDF URL
        pdf_info = data.get("openAccessPdf")
        pdf_url = pdf_info.get("url", "") if pdf_info else ""
        
        # Get year and construct date
        year = data.get("year")
        published = f"{year}-01-01" if year else ""
        
        # Get authors
        authors = []
        for author in data.get("authors", []):
            name = author.get("name", "")
            if name:
                authors.append(name)
        
        # Get citation count
        citations = data.get("citationCount", 0) or 0
        
        # Extract keywords from title and abstract
        keywords = self._extract_keywords(title + " " + abstract)
        
        return Paper(
            id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            pdf_url=pdf_url,
            published=published,
            source="semantic_scholar",
            citations=citations,
            keywords=keywords[:20]
        )
    
    def fetch_references(self, paper: Paper) -> List[Paper]:
        """Fetch papers cited by the given paper."""
        if not paper.id:
            return []
        
        papers = []
        
        try:
            session = self._requests_session()
            url = f"{self.BASE_URL}/paper/{paper.id}/references"
            params = {
                "fields": "paperId,title,authors,year,abstract,url,openAccessPdf,citationCount",
                "limit": 20
            }
            
            resp = session.get(url, params=params, timeout=30)
            time.sleep(0.3)
            
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    cited_paper = item.get("citedPaper")
                    if cited_paper:
                        parsed = self._parse_paper(cited_paper)
                        if parsed:
                            papers.append(parsed)
                            
        except Exception:
            pass
        
        return papers


# Register the source
register_source("semantic_scholar", SemanticScholarSource)
