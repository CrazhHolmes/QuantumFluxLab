"""
Quantum-Flux Lab - Open Source Physics Research Platform

Modules:
    scraper: Open-access research paper scraper
    api: FastAPI REST API wrapper

MIT License - 2026 Quantum-Flux Lab Contributors
"""

__version__ = "1.0.0"
__author__ = "Quantum-Flux Lab Contributors"
__license__ = "MIT"

from .scraper import QuantumFluxScraper, ResearchPaper, OpenAccessFilter

__all__ = [
    'QuantumFluxScraper',
    'ResearchPaper',
    'OpenAccessFilter'
]
