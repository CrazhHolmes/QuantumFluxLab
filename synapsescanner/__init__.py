"""SynapseScanner - Universal Research Scanner & Reality-Breaker."""
__version__ = "1.4.0"

# Make key components available at package level
from .sources import Paper, BaseSource, Connection, get_source, list_sources

__all__ = [
    "__version__",
    "Paper",
    "BaseSource", 
    "Connection",
    "get_source",
    "list_sources",
]
