"""Multi-source adapter architecture for SynapseScanner."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Paper:
    """Standardized paper representation across all sources."""
    id: str                          # source-specific ID
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    url: str = ""                    # direct link
    pdf_url: str = ""                # if available
    published: str = ""              # ISO date string
    source: str = ""                 # 'arxiv', 'semantic_scholar', etc.
    citations: int = 0               # 0 if unknown
    references: List[str] = field(default_factory=list)  # paper IDs this paper cites
    keywords: List[str] = field(default_factory=list)    # extracted keywords
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "published": self.published,
            "source": self.source,
            "citations": self.citations,
            "references": self.references,
            "keywords": self.keywords,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Paper":
        """Create Paper from dictionary."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            authors=data.get("authors", []),
            abstract=data.get("abstract", ""),
            url=data.get("url", ""),
            pdf_url=data.get("pdf_url", ""),
            published=data.get("published", ""),
            source=data.get("source", ""),
            citations=data.get("citations", 0),
            references=data.get("references", []),
            keywords=data.get("keywords", []),
        )


@dataclass
class Connection:
    """Represents a connection between two papers."""
    paper_a: Paper
    paper_b: Paper
    strength: int                    # 1-10
    reason: str                      # e.g., "Shared authors: Smith et al."


class BaseSource(ABC):
    """Abstract base class for all paper sources."""
    
    def __init__(self, name: str):
        self.name = name
        self._session = None
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search for papers matching the query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        pass
    
    @abstractmethod
    def fetch_references(self, paper: Paper) -> List[Paper]:
        """Fetch papers cited by the given paper.
        
        Args:
            paper: Paper to fetch references for
            
        Returns:
            List of Paper objects (may be empty if not supported)
        """
        pass
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for cross-referencing.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords (lowercase)
        """
        # Simple keyword extraction - can be enhanced with NLP
        common_words = {
            'the', 'and', 'or', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'we', 'our', 'us', 'you',
            'they', 'them', 'their', 'it', 'its', 'he', 'she', 'his', 'her',
            'paper', 'study', 'research', 'method', 'methods', 'result',
            'results', 'conclusion', 'conclusions', 'using', 'based', 'new',
            'approach', 'proposed', 'analysis', 'data', 'show', 'shown'
        }
        
        # Split and clean
        words = text.lower().split()
        keywords = []
        for word in words:
            # Remove punctuation
            clean = ''.join(c for c in word if c.isalnum())
            if len(clean) > 3 and clean not in common_words:
                keywords.append(clean)
        
        # Return unique keywords
        return list(set(keywords))
    
    def _requests_session(self):
        """Get or create a requests session for connection pooling."""
        if self._session is None:
            import requests
            self._session = requests.Session()
        return self._session


# Source registry
SOURCE_REGISTRY: Dict[str, type] = {}


def register_source(name: str, source_class: type):
    """Register a source class."""
    SOURCE_REGISTRY[name] = source_class


def get_source(name: str) -> Optional[BaseSource]:
    """Get a source instance by name."""
    if name in SOURCE_REGISTRY:
        return SOURCE_REGISTRY[name](name)
    return None


def list_sources() -> List[str]:
    """List all available source names."""
    return list(SOURCE_REGISTRY.keys())
