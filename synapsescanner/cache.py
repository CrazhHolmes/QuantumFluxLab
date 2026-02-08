"""SQLite local cache for SynapseScanner."""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from .sources import Paper


class Cache:
    """SQLite cache for paper data and search history."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default location: ~/.synapse/cache.db
            home = Path.home()
            cache_dir = home / ".synapse"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(cache_dir / "cache.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT,
                    authors TEXT,  -- JSON array
                    abstract TEXT,
                    url TEXT,
                    pdf_url TEXT,
                    published TEXT,
                    citations INTEGER DEFAULT 0,
                    references_data TEXT,  -- JSON array
                    keywords TEXT,  -- JSON array
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id, source)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    source TEXT NOT NULL,
                    max_results INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_papers_source 
                ON papers(source)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_queries_timestamp 
                ON queries(timestamp)
            """)
            
            conn.commit()
    
    def save_papers(self, papers: List[Paper]):
        """Save papers to cache."""
        with sqlite3.connect(self.db_path) as conn:
            for paper in papers:
                conn.execute("""
                    INSERT OR REPLACE INTO papers
                    (id, source, title, authors, abstract, url, pdf_url, 
                     published, citations, references_data, keywords, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper.id,
                    paper.source,
                    paper.title,
                    json.dumps(paper.authors),
                    paper.abstract,
                    paper.url,
                    paper.pdf_url,
                    paper.published,
                    paper.citations,
                    json.dumps(paper.references),
                    json.dumps(paper.keywords),
                    datetime.now().isoformat()
                ))
            conn.commit()
    
    def get_cached(self, query: str, source: str, max_age_hours: int = 24) -> Optional[List[Paper]]:
        """Get cached papers for a query if not expired.
        
        Args:
            query: Search query string
            source: Source name
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            List of papers if cache hit, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            # Check if we have a recent query entry
            cutoff = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
            
            cursor = conn.execute("""
                SELECT id FROM queries
                WHERE query = ? AND source = ? AND timestamp > ?
                ORDER BY timestamp DESC LIMIT 1
            """, (query, source, cutoff))
            
            if not cursor.fetchone():
                return None
            
            # Get papers for this query - simplified: return recent papers from this source
            cursor = conn.execute("""
                SELECT * FROM papers
                WHERE source = ? AND fetched_at > ?
                ORDER BY fetched_at DESC
            """, (source, cutoff))
            
            rows = cursor.fetchall()
            if not rows:
                return None
            
            papers = []
            for row in rows:
                paper = self._row_to_paper(row)
                papers.append(paper)
            
            return papers
    
    def record_query(self, query: str, source: str, max_results: int, result_count: int):
        """Record a query in the history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO queries (query, source, max_results, result_count, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (query, source, max_results, result_count, datetime.now().isoformat()))
            conn.commit()
    
    def get_paper_by_id(self, paper_id: str, source: str) -> Optional[Paper]:
        """Get a specific paper by ID and source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM papers WHERE id = ? AND source = ?",
                (paper_id, source)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_paper(row)
            return None
    
    def get_all_papers(self, limit: int = 1000) -> List[Paper]:
        """Get all cached papers."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM papers ORDER BY fetched_at DESC LIMIT ?",
                (limit,)
            )
            return [self._row_to_paper(row) for row in cursor.fetchall()]
    
    def clear_cache(self):
        """Clear all cached data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM papers")
            conn.execute("DELETE FROM queries")
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            paper_count = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            query_count = conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            
            # Count by source
            cursor = conn.execute("""
                SELECT source, COUNT(*) FROM papers GROUP BY source
            """)
            by_source = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_papers": paper_count,
                "total_queries": query_count,
                "by_source": by_source,
                "db_path": self.db_path
            }
    
    def _row_to_paper(self, row) -> Paper:
        """Convert database row to Paper object."""
        return Paper(
            id=row[0],
            source=row[1],
            title=row[2],
            authors=json.loads(row[3]) if row[3] else [],
            abstract=row[4] or "",
            url=row[5] or "",
            pdf_url=row[6] or "",
            published=row[7] or "",
            citations=row[8] or 0,
            references=json.loads(row[9]) if row[9] else [],
            keywords=json.loads(row[10]) if row[10] else []
        )


# Global cache instance
_cache_instance: Optional[Cache] = None


def get_cache(db_path: Optional[str] = None) -> Cache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache(db_path)
    return _cache_instance
