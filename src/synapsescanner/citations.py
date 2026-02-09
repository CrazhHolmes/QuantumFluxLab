"""Citation tracking for SynapseScanner v1.4.0"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Citation:
    """Represents a citation of a paper."""
    citing_paper_id: str
    citing_paper_title: str
    citing_paper_url: str
    citing_authors: List[str]
    citation_date: str
    citation_count: int = 1


class CitationTracker:
    """Track who cited your discovered papers."""
    
    def __init__(self):
        self.cache = {}
    
    def get_citations(self, paper_id: str, source: str) -> List[Citation]:
        """
        Fetch papers that cite the given paper.
        
        Args:
            paper_id: The paper ID to check
            source: The source (arxiv, semantic_scholar, etc.)
            
        Returns:
            List of Citation objects
        """
        if source == "semantic_scholar":
            return self._get_semantic_scholar_citations(paper_id)
        elif source == "arxiv":
            # ArXiv doesn't have citation API, use Semantic Scholar
            return self._get_semantic_scholar_citations(f"ARXIV:{paper_id}")
        elif source == "pubmed":
            return self._get_pubmed_citations(paper_id)
        else:
            return []
    
    def _get_semantic_scholar_citations(self, paper_id: str) -> List[Citation]:
        """Fetch citations from Semantic Scholar API."""
        citations = []
        
        try:
            import requests
            
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
            params = {
                "fields": "paperId,title,authors,year,url,citationCount",
                "limit": 20
            }
            
            resp = requests.get(url, params=params, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", []):
                    citing = item.get("citingPaper", {})
                    if citing:
                        citations.append(Citation(
                            citing_paper_id=citing.get("paperId", ""),
                            citing_paper_title=citing.get("title", "Unknown"),
                            citing_paper_url=citing.get("url", ""),
                            citing_authors=[a.get("name", "") for a in citing.get("authors", [])],
                            citation_date=str(citing.get("year", "")),
                            citation_count=citing.get("citationCount", 0)
                        ))
        except Exception as e:
            pass
        
        return citations
    
    def _get_pubmed_citations(self, pmid: str) -> List[Citation]:
        """Fetch citations from PubMed (limited support)."""
        # PubMed's citation API is more complex
        # Return empty for now - can be enhanced later
        return []
    
    def calculate_impact_score(self, paper) -> Dict:
        """
        Calculate impact metrics for a paper.
        
        Returns:
            Dict with metrics like total_citations, h_index_estimate, etc.
        """
        citations = self.get_citations(paper.id, paper.source)
        
        if not citations:
            return {
                "total_citations": paper.citations,
                "recent_citations": 0,
                "high_impact_citations": 0,
                "impact_score": 0
            }
        
        # Count recent citations (last 2 years)
        current_year = datetime.now().year
        recent_citations = sum(
            1 for c in citations 
            if c.citation_date and int(c.citation_date) >= current_year - 2
        )
        
        # Count high-impact citations (papers with 10+ citations themselves)
        high_impact = sum(1 for c in citations if c.citation_count >= 10)
        
        # Calculate impact score (0-100)
        # Based on: total citations (40%), recency (30%), quality of citing papers (30%)
        total = paper.citations or len(citations)
        score = min(100, int(
            (min(total / 100, 1) * 40) +  # Max 40 pts for 100+ citations
            (min(recent_citations / 20, 1) * 30) +  # Max 30 pts for 20+ recent
            (min(high_impact / 10, 1) * 30)  # Max 30 pts for 10+ high-impact
        ))
        
        return {
            "total_citations": total,
            "recent_citations": recent_citations,
            "high_impact_citations": high_impact,
            "impact_score": score
        }


def format_citation_report(citations: List[Citation], paper_title: str) -> str:
    """Format citations for CLI display."""
    lines = [
        f"\n  ╭── Citation Report: {paper_title[:40]}{'...' if len(paper_title) > 40 else ''} ──╮",
    ]
    
    if not citations:
        lines.append("  │  No citations found (yet!)")
    else:
        lines.append(f"  │  Found {len(citations)} papers citing this work:")
        lines.append("  │")
        
        for i, cite in enumerate(citations[:5], 1):
            authors = ", ".join(cite.citing_authors[:2])
            if len(cite.citing_authors) > 2:
                authors += " et al."
            
            impact = "🔥" if cite.citation_count > 50 else "📈" if cite.citation_count > 10 else "📄"
            lines.append(f"  │  {impact} {cite.citing_paper_title[:50]}...")
            lines.append(f"  │     by {authors} ({cite.citation_date})")
            lines.append("  │")
    
    lines.append("  ╰──────────────────────────────────────────────────────────╯")
    
    return "\n".join(lines)
