"""Test paper source adapters."""
import pytest
from synapsescanner.sources import Paper, get_source, list_sources
from synapsescanner.sources.arxiv import ArXivSource


class TestPaper:
    """Test Paper dataclass."""
    
    def test_paper_creation(self):
        paper = Paper(
            id="1234.5678",
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            abstract="This is a test abstract.",
            url="https://arxiv.org/abs/1234.5678",
            source="arxiv"
        )
        assert paper.id == "1234.5678"
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.source == "arxiv"
    
    def test_paper_to_dict(self):
        paper = Paper(
            id="1234.5678",
            title="Test Paper",
            authors=["John Doe"],
            source="arxiv"
        )
        data = paper.to_dict()
        assert data["id"] == "1234.5678"
        assert data["title"] == "Test Paper"
        assert isinstance(data["authors"], list)
    
    def test_paper_from_dict(self):
        data = {
            "id": "1234.5678",
            "title": "Test Paper",
            "authors": ["John Doe"],
            "abstract": "Test",
            "url": "https://test.com",
            "pdf_url": "",
            "published": "2024-01-01",
            "source": "arxiv",
            "citations": 10,
            "references": [],
            "keywords": ["test"]
        }
        paper = Paper.from_dict(data)
        assert paper.id == "1234.5678"
        assert paper.citations == 10


class TestSources:
    """Test source adapters."""
    
    def test_arxiv_source_exists(self):
        source = get_source("arxiv")
        assert source is not None
        assert isinstance(source, ArXivSource)
    
    def test_list_sources(self):
        sources = list_sources()
        assert "arxiv" in sources
        assert isinstance(sources, list)
    
    def test_arxiv_search(self):
        """Integration test - may fail without network."""
        source = ArXivSource()
        try:
            papers = source.search("quantum", limit=1)
            assert isinstance(papers, list)
            if papers:
                assert isinstance(papers[0], Paper)
                assert papers[0].source == "arxiv"
        except Exception:
            pytest.skip("Network unavailable or ArXiv API error")
