"""Test citation tracking module."""
import pytest
from synapsescanner.citations import Citation, CitationTracker


class TestCitation:
    """Test Citation dataclass."""
    
    def test_citation_creation(self):
        cite = Citation(
            citing_paper_id="abc123",
            citing_paper_title="Citing Paper",
            citing_paper_url="https://example.com",
            citing_authors=["Author One"],
            citation_date="2024"
        )
        assert cite.citing_paper_id == "abc123"
        assert cite.citation_count == 1


class TestCitationTracker:
    """Test CitationTracker."""
    
    def test_tracker_creation(self):
        tracker = CitationTracker()
        assert tracker is not None
    
    def test_calculate_impact_score_no_citations(self):
        tracker = CitationTracker()
        
        # Create mock paper
        class MockPaper:
            id = "1234"
            source = "arxiv"
            citations = 0
        
        paper = MockPaper()
        metrics = tracker.calculate_impact_score(paper)
        
        assert "total_citations" in metrics
        assert "impact_score" in metrics
        assert metrics["impact_score"] == 0
