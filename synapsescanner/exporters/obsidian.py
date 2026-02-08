"""Obsidian markdown exporter for SynapseScanner."""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from . import BaseExporter
from ..sources import Paper, Connection


class ObsidianExporter(BaseExporter):
    """Export papers to Obsidian-compatible markdown with YAML frontmatter."""
    
    def __init__(self, output_path: Optional[str] = None):
        if output_path is None:
            # Default to ~/SynapseNotes
            output_path = os.path.expanduser("~/SynapseNotes")
        super().__init__(output_path)
    
    def export(self, papers: List[Paper], connections: Optional[List[Connection]] = None,
               query: str = "") -> str:
        """Export papers to Obsidian markdown files.
        
        Returns summary of exported files.
        """
        Path(self.output_path).mkdir(parents=True, exist_ok=True)
        
        exported = []
        
        for paper in papers:
            filename = self._sanitize_filename(paper.title)
            filepath = os.path.join(self.output_path, f"{filename}.md")
            
            content = self._format_paper(paper, query)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            exported.append(filename)
        
        # Export connections if any
        if connections:
            conn_filename = f"connections_{self._sanitize_filename(query) or 'all'}"
            conn_filepath = os.path.join(self.output_path, f"{conn_filename}.md")
            
            conn_content = self._format_connections(connections, query)
            with open(conn_filepath, 'w', encoding='utf-8') as f:
                f.write(conn_content)
            
            exported.append(conn_filename)
        
        return f"Exported {len(exported)} files to {self.output_path}"
    
    def export_to_string(self, papers: List[Paper], connections: Optional[List[Connection]] = None,
                        query: str = "") -> str:
        """Export papers to a single markdown string (for stdout redirection)."""
        sections = []
        
        for paper in papers:
            sections.append(self._format_paper(paper, query))
        
        if connections:
            sections.append(self._format_connections(connections, query))
        
        return "\n\n---\n\n".join(sections)
    
    def _format_paper(self, paper: Paper, query: str) -> str:
        """Format a single paper as Obsidian markdown with YAML frontmatter."""
        # Extract tags from keywords
        tags = paper.keywords[:10] if paper.keywords else []
        
        # Add query as a tag if provided
        if query:
            query_tag = re.sub(r'[^\w]', '_', query.lower())
            if query_tag not in tags:
                tags.append(query_tag)
        
        # Ensure source is a tag
        if paper.source and paper.source not in tags:
            tags.append(paper.source)
        
        # Build YAML frontmatter
        lines = ["---"]
        lines.append(f'title: "{self._escape_yaml(paper.title)}"')
        lines.append(f'authors: {paper.authors}')
        lines.append(f'source: {paper.source}')
        lines.append(f'paper_id: "{paper.id}"')
        lines.append(f'url: {paper.url}')
        if paper.pdf_url:
            lines.append(f'pdf_url: {paper.pdf_url}')
        if paper.published:
            lines.append(f'published: {paper.published}')
        if paper.citations:
            lines.append(f'citations: {paper.citations}')
        lines.append(f'tags: {tags}')
        lines.append(f'fetched: {datetime.now().strftime("%Y-%m-%d")}')
        lines.append("---")
        lines.append("")
        
        # Abstract
        if paper.abstract:
            lines.append("## Abstract")
            lines.append("")
            lines.append(paper.abstract)
            lines.append("")
        
        # Links section
        lines.append("## Links")
        lines.append(f"- [Source]({paper.url})")
        if paper.pdf_url:
            lines.append(f"- [PDF]({paper.pdf_url})")
        lines.append("")
        
        # Notes section (empty for user to fill)
        lines.append("## Notes")
        lines.append("")
        lines.append("_Add your notes here..._")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_connections(self, connections: List[Connection], query: str) -> str:
        """Format connections as markdown."""
        lines = ["---"]
        lines.append(f'title: "Hidden Connections - {self._escape_yaml(query) or "Research"}"')
        lines.append(f'type: connections')
        lines.append(f'fetched: {datetime.now().strftime("%Y-%m-%d")}')
        lines.append("---")
        lines.append("")
        lines.append("# Hidden Connections")
        lines.append("")
        
        for conn in connections:
            lines.append(f"## {conn.paper_a.title} ↔ {conn.paper_b.title}")
            lines.append("")
            lines.append(f"**Strength:** {'★' * conn.strength}{'☆' * (10 - conn.strength)}")
            lines.append("")
            lines.append(f"**Reason:** {conn.reason}")
            lines.append("")
            lines.append(f"- [{conn.paper_a.title}]({self._sanitize_filename(conn.paper_a.title)}.md)")
            lines.append(f"- [{conn.paper_b.title}]({self._sanitize_filename(conn.paper_b.title)}.md)")
            lines.append("")
        
        return "\n".join(lines)
    
    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename."""
        # Remove/replace unsafe characters
        safe = re.sub(r'[^\w\s-]', '', title)
        safe = re.sub(r'[-\s]+', '_', safe)
        # Limit length
        safe = safe[:50].strip('_')
        if not safe:
            safe = "untitled"
        return safe.lower()
    
    def _escape_yaml(self, text: str) -> str:
        """Escape special characters for YAML."""
        return text.replace('"', '\\"').replace('\\', '\\\\')
