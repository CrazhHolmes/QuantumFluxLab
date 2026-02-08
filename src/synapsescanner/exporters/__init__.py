"""Export modules for SynapseScanner."""
from typing import List, Dict, Any, Optional
from ..sources import Paper, Connection


class BaseExporter:
    """Base class for exporters."""
    
    def __init__(self, output_path: Optional[str] = None):
        self.output_path = output_path
    
    def export(self, papers: List[Paper], connections: Optional[List[Connection]] = None) -> str:
        """Export papers to the target format.
        
        Args:
            papers: List of papers to export
            connections: Optional list of connections between papers
            
        Returns:
            String representation of the export
        """
        raise NotImplementedError
