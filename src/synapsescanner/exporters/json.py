"""JSON exporter for SynapseScanner."""
import json
from datetime import datetime
from typing import List, Optional
from . import BaseExporter
from ..sources import Paper, Connection


class JSONExporter(BaseExporter):
    """Export papers to JSON format for piping and programmatic use."""
    
    def export(self, papers: List[Paper], connections: Optional[List[Connection]] = None,
               include_raw: bool = True) -> str:
        """Export papers to JSON string.
        
        Args:
            papers: List of papers to export
            connections: Optional list of connections between papers
            include_raw: Include full paper data (not just IDs) in connections
            
        Returns:
            JSON string
        """
        data = {
            "version": "1.3.0",
            "generated_at": datetime.now().isoformat(),
            "count": len(papers),
            "papers": [paper.to_dict() for paper in papers]
        }
        
        if connections:
            if include_raw:
                data["connections"] = [
                    {
                        "paper_a": conn.paper_a.to_dict(),
                        "paper_b": conn.paper_b.to_dict(),
                        "strength": conn.strength,
                        "reason": conn.reason
                    }
                    for conn in connections
                ]
            else:
                data["connections"] = [
                    {
                        "paper_a_id": conn.paper_a.id,
                        "paper_a_source": conn.paper_a.source,
                        "paper_b_id": conn.paper_b.id,
                        "paper_b_source": conn.paper_b.source,
                        "strength": conn.strength,
                        "reason": conn.reason
                    }
                    for conn in connections
                ]
            data["connection_count"] = len(connections)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_compact(self, papers: List[Paper], connections: Optional[List[Connection]] = None) -> str:
        """Export to compact JSON (single line) for piping."""
        data = {
            "version": "1.3.0",
            "generated_at": datetime.now().isoformat(),
            "count": len(papers),
            "papers": [paper.to_dict() for paper in papers]
        }
        
        if connections:
            data["connections"] = [
                {
                    "paper_a_id": conn.paper_a.id,
                    "paper_b_id": conn.paper_b.id,
                    "strength": conn.strength,
                    "reason": conn.reason
                }
                for conn in connections
            ]
        
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
