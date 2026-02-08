"""Cross-reference engine for finding hidden connections between papers."""
from typing import List, Set, Tuple
from collections import defaultdict
from .sources import Paper, Connection


def find_connections(papers: List[Paper], keyword_threshold: int = 3) -> List[Connection]:
    """Find connections between papers from different sources.
    
    Detects connections based on:
    - Shared authors
    - Shared keywords (case-insensitive)
    
    Args:
        papers: List of papers to analyze
        keyword_threshold: Minimum number of shared keywords for a connection
        
    Returns:
        List of Connection objects
    """
    connections = []
    
    # Group papers by source for comparison
    papers_by_source = defaultdict(list)
    for paper in papers:
        papers_by_source[paper.source].append(paper)
    
    sources = list(papers_by_source.keys())
    
    # Compare papers from different sources
    for i, source_a in enumerate(sources):
        for source_b in sources[i+1:]:
            for paper_a in papers_by_source[source_a]:
                for paper_b in papers_by_source[source_b]:
                    strength, reason = _calculate_connection(
                        paper_a, paper_b, keyword_threshold
                    )
                    
                    if strength > 0:
                        connections.append(Connection(
                            paper_a=paper_a,
                            paper_b=paper_b,
                            strength=strength,
                            reason=reason
                        ))
    
    # Sort by strength (descending)
    connections.sort(key=lambda c: c.strength, reverse=True)
    
    return connections


def _calculate_connection(paper_a: Paper, paper_b: Paper, 
                          keyword_threshold: int) -> Tuple[int, str]:
    """Calculate connection strength between two papers.
    
    Returns:
        Tuple of (strength 1-10, reason string)
    """
    strength = 0
    reasons = []
    
    # Check for shared authors
    authors_a = {a.lower() for a in paper_a.authors}
    authors_b = {b.lower() for b in paper_b.authors}
    shared_authors = authors_a & authors_b
    
    if shared_authors:
        # Strength based on number of shared authors
        author_strength = min(len(shared_authors) * 3, 7)
        strength += author_strength
        author_names = list(shared_authors)[:3]
        reasons.append(f"Shared authors: {', '.join(author_names)}")
    
    # Check for shared keywords
    keywords_a = {k.lower() for k in paper_a.keywords}
    keywords_b = {k.lower() for k in paper_b.keywords}
    shared_keywords = keywords_a & keywords_b
    
    if len(shared_keywords) >= keyword_threshold:
        # Strength based on number of shared keywords
        keyword_strength = min(len(shared_keywords), 5)
        strength += keyword_strength
        keyword_list = list(shared_keywords)[:5]
        reasons.append(f"Shared keywords: {', '.join(keyword_list)}")
    
    # Check for title similarity (simple word overlap)
    title_words_a = set(paper_a.title.lower().split())
    title_words_b = set(paper_b.title.lower().split())
    # Remove common words
    common_words = {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'to', 'for',
                    'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were',
                    'study', 'analysis', 'research', 'using', 'based'}
    title_words_a -= common_words
    title_words_b -= common_words
    
    shared_title_words = title_words_a & title_words_b
    if len(shared_title_words) >= 2:
        title_strength = min(len(shared_title_words), 3)
        strength += title_strength
        reasons.append(f"Similar topics: {', '.join(list(shared_title_words)[:3])}")
    
    # Cap strength at 10
    strength = min(strength, 10)
    
    if strength == 0:
        return 0, ""
    
    # Build reason string
    reason = "; ".join(reasons)
    
    return strength, reason


def find_citation_trails(papers: List[Paper]) -> List[Tuple[Paper, Paper]]:
    """Find citation trails (Paper A → cited by → Paper B).
    
    Args:
        papers: List of papers to analyze
        
    Returns:
        List of (citing_paper, cited_paper) tuples
    """
    trails = []
    
    # Build lookup by ID
    paper_by_id = {}
    for paper in papers:
        if paper.id:
            paper_by_id[(paper.id, paper.source)] = paper
    
    # Check each paper's references
    for paper in papers:
        for ref_id in paper.references:
            # Look for referenced paper in our set
            for source in set(p.source for p in papers):
                key = (ref_id, source)
                if key in paper_by_id:
                    trails.append((paper, paper_by_id[key]))
                    break
    
    return trails
