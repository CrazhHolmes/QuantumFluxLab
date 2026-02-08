"""BioRxiv source adapter for SynapseScanner."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from . import Paper, BaseSource, register_source


class BioRxivSource(BaseSource):
    """BioRxiv/MedRxiv paper source using the public API."""
    
    BASE_URL = "https://api.biorxiv.org/correspondence"
    DETAILS_URL = "https://api.biorxiv.org/details"
    
    def __init__(self, name: str = "biorxiv"):
        super().__init__(name)
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search BioRxiv for papers matching the query."""
        papers = []
        
        try:
            session = self._requests_session()
            
            # BioRxiv API works with date ranges - fetch recent papers
            # and filter by query locally
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Last year
            
            # Try biorxiv first
            papers.extend(self._fetch_from_server(
                session, "biorxiv", start_date, end_date, query, limit
            ))
            
            # If we need more, try medrxiv
            if len(papers) < limit:
                remaining = limit - len(papers)
                papers.extend(self._fetch_from_server(
                    session, "medrxiv", start_date, end_date, query, remaining
                ))
                
        except Exception:
            pass
        
        return papers[:limit]
    
    def _fetch_from_server(self, session, server: str, start_date: datetime,
                          end_date: datetime, query: str, limit: int) -> List[Paper]:
        """Fetch papers from a specific server (biorxiv/medrxiv)."""
        papers = []
        
        try:
            # Format dates as YYYY-MM-DD
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            # Use the details endpoint with date range
            url = f"{self.DETAILS_URL}/{server}/{start_str}/{end_str}"
            
            resp = session.get(url, timeout=60)
            resp.raise_for_status()
            
            data = resp.json()
            collection = data.get("collection", [])
            
            # Filter by query if provided
            query_lower = query.lower() if query else ""
            
            for item in collection:
                title = item.get("title", "")
                abstract = item.get("abstract", "") or ""
                
                # Filter by query
                if query_lower:
                    text = (title + " " + abstract).lower()
                    if query_lower not in text:
                        continue
                
                paper = self._parse_paper(item, server)
                if paper:
                    papers.append(paper)
                    
                if len(papers) >= limit:
                    break
                    
        except Exception:
            pass
        
        return papers
    
    def _parse_paper(self, data: Dict[str, Any], server: str) -> Paper:
        """Parse BioRxiv/MedRxiv data into a Paper."""
        doi = data.get("doi", "")
        title = data.get("title", "Unknown")
        abstract = data.get("abstract", "") or ""
        
        # Get authors
        authors = []
        author_string = data.get("authors", "")
        if author_string:
            # Authors are comma-separated
            for name in author_string.split(";"):
                name = name.strip()
                if name:
                    authors.append(name)
        
        # Get dates
        date_str = data.get("date", "")
        published = ""
        if date_str:
            try:
                # Try to parse and reformat
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                published = dt.strftime("%Y-%m-%d")
            except ValueError:
                published = date_str
        
        # Construct URLs
        url = f"https://www.{server}.org/content/{doi}" if doi else ""
        pdf_url = f"https://www.{server}.org/content/{doi}.full.pdf" if doi else ""
        
        # Extract keywords
        keywords = self._extract_keywords(title + " " + abstract)
        
        return Paper(
            id=doi,
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            pdf_url=pdf_url,
            published=published,
            source=server,  # "biorxiv" or "medrxiv"
            citations=0,
            keywords=keywords[:20]
        )
    
    def fetch_references(self, paper: Paper) -> List[Paper]:
        """BioRxiv doesn't provide citation/reference data."""
        return []


# Register the source
register_source("biorxiv", BioRxivSource)
