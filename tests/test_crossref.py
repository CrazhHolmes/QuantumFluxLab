"""Test cross-reference engine."""
import pytest
from synapsescanner.sources import Paper
from synapsescanner.crossref import find_connections


class TestCrossRef:
    """Test cross-reference detection."""
    
    def test_find_connections_empty(self):
        papers = []
        connections = find_connections(papers)
        assert connections == []
    
    def test_find_connections_single_paper(self):
        paper = Paper(
            id="1",
            title="Test",
            source="arxiv"
        )
        connections = find_connections([paper])
        assert connections == []
    
    def test_find_connections_shared_authors(self):
        paper1 = Paper(
            id="1",
            title="Paper One",
            authors=["John Smith", "Jane Doe"],
            abstract="About quantum computing",
            source="arxiv"
        )
        paper2 = Paper(
            id="2",
            title="Paper Two",
            authors=["John Smith", "Bob Wilson"],
            abstract="About machine learning",
            source="semantic_scholar"
        )
        
        connections = find_connections([paper1, paper2])
        
        # Should find connection due to shared author
        assert len(connections) > 0
        assert connections[0].paper_a.id == "1"
        assert connections[0].paper_b.id == "2"
        assert "john smith" in connections[0].reason.lower()
