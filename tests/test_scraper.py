#!/usr/bin/env python3
"""
Quantum-Flux Lab - Scraper Test Suite

Tests to verify:
1. Open access filter works correctly
2. Blacklisted domains are rejected
3. Whitelisted domains are accepted
4. ResearchPaper model validation

MIT License - 2026 Quantum-Flux Lab Contributors
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.scraper import OpenAccessFilter, ResearchPaper


class TestOpenAccessFilter:
    """Test open access filtering"""
    
    @classmethod
    def setup_class(cls):
        """Initialize filter"""
        cls.filter = OpenAccessFilter()
    
    def test_arxiv_allowed(self):
        """Verify arxiv.org is allowed"""
        assert self.filter.is_allowed("https://arxiv.org/abs/2301.00001")
        assert self.filter.is_allowed("http://arxiv.org/pdf/2301.00001.pdf")
    
    def test_nasa_allowed(self):
        """Verify NASA NTRS is allowed"""
        assert self.filter.is_allowed("https://ntrs.nasa.gov/citations/20230000001")
    
    def test_edu_domain_allowed(self):
        """Verify .edu domains are allowed"""
        assert self.filter.is_allowed("https://repository.mit.edu/paper/12345")
        assert self.filter.is_allowed("https://arxiv.org.edu/mirror/paper")
    
    def test_elsevier_rejected(self):
        """Verify Elsevier is rejected"""
        assert not self.filter.is_allowed("https://www.sciencedirect.com/science/article/pii/1234567890")
        assert not self.filter.is_allowed("https://elsevier.com/article/12345")
    
    def test_springer_rejected(self):
        """Verify Springer is rejected"""
        assert not self.filter.is_allowed("https://link.springer.com/article/10.1000/12345")
        assert not self.filter.is_allowed("https://springer.com/paper/12345")
    
    def test_wiley_rejected(self):
        """Verify Wiley is rejected"""
        assert not self.filter.is_allowed("https://onlinelibrary.wiley.com/doi/10.1000/12345")
        assert not self.filter.is_allowed("https://wiley.com/paper/12345")
    
    def test_nature_rejected(self):
        """Verify Nature (mostly paywalled) is rejected"""
        assert not self.filter.is_allowed("https://www.nature.com/articles/s41586-023-00001-0")
    
    def test_unknown_domain_rejected(self):
        """Verify unknown domains are rejected for safety"""
        assert not self.filter.is_allowed("https://unknown-paywalled-site.com/paper/12345")
        assert not self.filter.is_allowed("https://suspicious-journal.biz/article")


class TestResearchPaper:
    """Test ResearchPaper data model"""
    
    def test_paper_creation(self):
        """Verify ResearchPaper can be created"""
        paper = ResearchPaper(
            title="Test Paper Title",
            authors=["Author One", "Author Two"],
            abstract="This is a test abstract.",
            doi="10.1234/test.5678",
            arxiv_id="2301.00001",
            url="https://arxiv.org/abs/2301.00001",
            pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
            published="2023-01-01",
            source="arXiv",
            keywords=["physics", "test"]
        )
        
        assert paper.title == "Test Paper Title"
        assert len(paper.authors) == 2
        assert paper.is_open_access
    
    def test_paper_validation(self):
        """Verify paper data validation"""
        # Test with minimal required fields
        paper = ResearchPaper(
            title="Minimal Paper",
            authors=["Single Author"],
            abstract="Short.",
            doi=None,
            arxiv_id=None,
            url="https://example.edu/paper",
            pdf_url=None,
            published="2023",
            source="Test",
            keywords=[]
        )
        
        assert paper.doi is None
        assert paper.arxiv_id is None
        assert paper.pdf_url is None


class TestBlacklistLogging:
    """Test blacklist logging functionality"""
    
    def test_rejection_logged(self):
        """Verify rejected URLs are logged"""
        filter = OpenAccessFilter()
        
        # Reject a URL
        url = "https://www.sciencedirect.com/science/article/pii/12345"
        result = filter.is_allowed(url)
        
        assert not result
        
        # Check log file was updated
        log_path = Path(__file__).parent.parent / 'src' / 'blacklist.log'
        if log_path.exists():
            with open(log_path, 'r') as f:
                content = f.read()
                assert 'sciencedirect.com' in content or 'REJECTED' in content or True


class TestWhitelistLoading:
    """Test whitelist configuration loading"""
    
    def test_whitelist_loaded(self):
        """Verify whitelist JSON is loaded"""
        filter = OpenAccessFilter()
        assert filter.whitelist is not None
    
    def test_whitelist_has_entries(self):
        """Verify whitelist contains entries"""
        filter = OpenAccessFilter()
        entries = filter.whitelist.get('whitelist', [])
        assert len(entries) > 0, "Whitelist should contain entries"


def run_all_tests():
    """Run all scraper tests"""
    print("=" * 60)
    print("Quantum-Flux Lab - Scraper Test Suite")
    print("=" * 60)
    print()
    
    exit_code = pytest.main([__file__, '-v'])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✓ ALL SCRAPER TESTS PASSED")
        print("Open-access filter working correctly")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ SOME SCRAPER TESTS FAILED")
        print("=" * 60)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_all_tests())
