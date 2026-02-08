"""PubMed/NCBI source adapter for SynapseScanner."""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from . import Paper, BaseSource, register_source


class PubMedSource(BaseSource):
    """PubMed paper source using E-utilities API."""
    
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    def __init__(self, name: str = "pubmed"):
        super().__init__(name)
        self.tool = "synapsescanner"
        self.email = "user@synapsescanner.local"  # Required by NCBI
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search PubMed for papers matching the query."""
        papers = []
        
        try:
            session = self._requests_session()
            
            # Step 1: Search for IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": limit,
                "retmode": "json",
                "tool": self.tool,
                "email": self.email
            }
            
            resp = session.get(self.ESEARCH_URL, params=search_params, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            idlist = data.get("esearchresult", {}).get("idlist", [])
            
            if not idlist:
                return papers
            
            # Step 2: Fetch summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(idlist),
                "retmode": "json",
                "tool": self.tool,
                "email": self.email
            }
            
            resp = session.get(self.ESUMMARY_URL, params=summary_params, timeout=30)
            resp.raise_for_status()
            
            summary_data = resp.json()
            
            # Step 3: Fetch abstracts (in batches)
            abstracts = self._fetch_abstracts(session, idlist)
            
            for pmid in idlist:
                doc = summary_data.get("result", {}).get(pmid, {})
                if doc:
                    paper = self._parse_paper(pmid, doc, abstracts.get(pmid, ""))
                    if paper:
                        papers.append(paper)
                        
        except Exception:
            pass
        
        return papers
    
    def _fetch_abstracts(self, session, pmids: List[str]) -> Dict[str, str]:
        """Fetch abstracts for given PMIDs."""
        abstracts = {}
        
        try:
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "tool": self.tool,
                "email": self.email
            }
            
            resp = session.get(self.EFETCH_URL, params=fetch_params, timeout=60)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.text)
            
            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                if pmid_elem is None:
                    continue
                    
                pmid = pmid_elem.text
                abstract_elem = article.find(".//Abstract/AbstractText")
                
                if abstract_elem is not None and abstract_elem.text:
                    abstracts[pmid] = abstract_elem.text
                    
        except Exception:
            pass
        
        return abstracts
    
    def _parse_paper(self, pmid: str, doc: Dict[str, Any], abstract: str) -> Paper:
        """Parse PubMed data into a Paper."""
        title = doc.get("title", "Unknown")
        
        # Get authors
        authors = []
        for author in doc.get("authors", []):
            name = author.get("name", "")
            if name:
                authors.append(name)
        
        # Get date
        pubdate = doc.get("pubdate", "")
        # Parse various PubMed date formats
        published = ""
        if pubdate:
            # Try to extract year
            parts = pubdate.split()
            if parts:
                year = parts[0]
                if year.isdigit() and len(year) == 4:
                    published = f"{year}-01-01"
        
        # Get article IDs
        article_ids = doc.get("articleids", [])
        doi = ""
        for aid in article_ids:
            if aid.get("idtype") == "doi":
                doi = aid.get("value", "")
                break
        
        # Construct URLs
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        pdf_url = f"https://doi.org/{doi}" if doi else ""
        
        # Extract keywords
        keywords = self._extract_keywords(title + " " + abstract)
        
        return Paper(
            id=pmid,
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            pdf_url=pdf_url,
            published=published,
            source="pubmed",
            citations=0,  # PubMed doesn't provide citation counts in basic API
            keywords=keywords[:20]
        )
    
    def fetch_references(self, paper: Paper) -> List[Paper]:
        """PubMed doesn't provide easy reference fetching."""
        return []


# Register the source
register_source("pubmed", PubMedSource)
