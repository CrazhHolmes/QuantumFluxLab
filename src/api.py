#!/usr/bin/env python3
"""
Quantum-Flux Lab - FastAPI Wrapper for Research Scraper

Provides REST API endpoints for:
- Searching open-access research papers
- Getting physics topic summaries
- Budget tracking
- Safety status

MIT License - 2026 Quantum-Flux Lab Contributors
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from scraper import QuantumFluxScraper, ResearchPaper, save_papers_to_json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Quantum-Flux Lab API",
    description="Open-access research scraper and lab management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper
scraper = QuantumFluxScraper()

# Paths
BASE_DIR = Path(__file__).parent.parent
BOM_PATH = BASE_DIR / 'bom' / 'BOM.csv'
LOGS_DIR = BASE_DIR / 'logs'


# ============================================================================
# Pydantic Models
# ============================================================================

class PaperResponse(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str]
    arxiv_id: Optional[str]
    url: str
    pdf_url: Optional[str]
    published: str
    source: str
    keywords: List[str]


class SearchResponse(BaseModel):
    query: str
    count: int
    papers: List[PaperResponse]


class BudgetItem(BaseModel):
    part_number: str
    description: str
    quantity: int
    unit_price: float
    source: str
    safety_rating: str
    notes: str


class BudgetResponse(BaseModel):
    total_cost: float
    budget_limit: float
    remaining: float
    items: List[BudgetItem]
    under_budget: bool


class SafetyStatus(BaseModel):
    status: str
    temperature: float
    ozone_level: float
    current_draw: float
    spl_level: float
    relay_status: str
    watchdog_status: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root with basic info"""
    return {
        "name": "Quantum-Flux Lab API",
        "version": "1.0.0",
        "license": "MIT",
        "budget_limit": 75.00,
        "endpoints": [
            "/search",
            "/topics",
            "/budget",
            "/safety",
            "/logs/{log_name}",
            "/docs"
        ]
    }


@app.get("/search", response_model=SearchResponse)
async def search_papers(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50),
    source: Optional[str] = Query("arxiv", description="Source: arxiv, nasa, or all")
):
    """
    Search open-access research papers
    
    - **q**: Search query string
    - **max_results**: Maximum number of results (1-50)
    - **source**: Data source ('arxiv', 'nasa', or 'all')
    """
    sources = {
        'arxiv': ['arxiv'],
        'nasa': ['nasa'],
        'all': ['arxiv', 'nasa']
    }.get(source, ['arxiv'])
    
    try:
        papers = scraper.search(q, sources=sources)
        papers = papers[:max_results]
        
        return SearchResponse(
            query=q,
            count=len(papers),
            papers=[
                PaperResponse(
                    title=p.title,
                    authors=p.authors,
                    abstract=p.abstract,
                    doi=p.doi,
                    arxiv_id=p.arxiv_id,
                    url=p.url,
                    pdf_url=p.pdf_url,
                    published=p.published,
                    source=p.source,
                    keywords=p.keywords
                )
                for p in papers
            ]
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics")
async def get_physics_topics():
    """Get papers organized by physics topics"""
    try:
        topics = scraper.search_physics_topics()
        
        result = {}
        for topic, papers in topics.items():
            result[topic] = [
                {
                    'title': p.title,
                    'authors': p.authors[:3],
                    'url': p.url,
                    'published': p.published
                }
                for p in papers
            ]
        
        return result
    except Exception as e:
        logger.error(f"Topics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/budget", response_model=BudgetResponse)
async def get_budget():
    """Get current BOM and budget status"""
    try:
        items = []
        total = 0.0
        
        if BOM_PATH.exists():
            with open(BOM_PATH, 'r') as f:
                # Skip header
                next(f)
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('TOTAL'):
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 8:
                        try:
                            qty = int(parts[2]) if parts[2] else 1
                            price = float(parts[3]) if parts[3] else 0.0
                            total += qty * price
                            
                            items.append(BudgetItem(
                                part_number=parts[0],
                                description=parts[1],
                                quantity=qty,
                                unit_price=price,
                                source=parts[4],
                                safety_rating=parts[6],
                                notes=parts[7]
                            ))
                        except ValueError:
                            continue
        
        budget_limit = 75.00
        
        return BudgetResponse(
            total_cost=round(total, 2),
            budget_limit=budget_limit,
            remaining=round(budget_limit - total, 2),
            items=items,
            under_budget=total <= budget_limit
        )
    except Exception as e:
        logger.error(f"Budget error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/safety")
async def get_safety_status():
    """Get current safety system status (simulated)"""
    # In real implementation, this would read from Arduino
    return {
        "system_status": "STANDBY",
        "sensors": {
            "temperature_1": {"value": 22.5, "unit": "°C", "status": "OK"},
            "temperature_2": {"value": 23.1, "unit": "°C", "status": "OK"},
            "ozone": {"value": 0.02, "unit": "ppm", "status": "OK"},
            "uv": {"value": 0.1, "unit": "mW/cm²", "status": "OK"},
            "current": {"value": 0.15, "unit": "A", "status": "OK"},
            "voltage": {"value": 11.8, "unit": "V", "status": "OK"},
            "spl": {"value": 45, "unit": "dB", "status": "OK"}
        },
        "safety_systems": {
            "relay": {"status": "CLOSED", "healthy": True},
            "watchdog": {"status": "ACTIVE", "timeout_ms": 100},
            "mosfet": {"status": "OFF", "gate_voltage": 0},
            "e_stop": {"status": "NOT_PRESSED", "armed": True}
        },
        "thresholds": {
            "temp_warning": 40,
            "temp_critical": 50,
            "ozone_warning": 0.05,
            "ozone_critical": 0.08,
            "current_warning": 0.8,
            "current_critical": 1.2,
            "spl_warning": 100,
            "spl_critical": 120
        }
    }


@app.get("/logs/{log_name}")
async def get_log(log_name: str):
    """
    Get research log content
    
    Available logs:
    - discovery
    - safety
    - timetravel
    """
    log_files = {
        'discovery': 'Log_discovery.log',
        'safety': 'Log_safety.log',
        'timetravel': 'Log_time_travel.log'
    }
    
    if log_name not in log_files:
        raise HTTPException(
            status_code=404,
            detail=f"Log not found. Available: {', '.join(log_files.keys())}"
        )
    
    log_path = LOGS_DIR / log_files[log_name]
    
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found on disk")
    
    try:
        with open(log_path, 'r') as f:
            content = f.read()
        return {"name": log_name, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/whitelist")
async def get_whitelist():
    """Get open-access whitelist configuration"""
    whitelist_path = Path(__file__).parent / 'whitelist.json'
    try:
        with open(whitelist_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Whitelist not found")


@app.get("/blacklist")
async def get_blacklist(limit: int = Query(100, ge=1, le=1000)):
    """Get recently blacklisted URLs"""
    blacklist_path = Path(__file__).parent / 'blacklist.log'
    try:
        with open(blacklist_path, 'r') as f:
            lines = f.readlines()
        
        # Return last N non-comment lines
        entries = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
        return {
            "total_entries": len(entries),
            "recent": entries[-limit:]
        }
    except FileNotFoundError:
        return {"total_entries": 0, "recent": []}


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("Quantum-Flux Lab API starting up")
    logger.info(f"BOM path: {BOM_PATH}")
    logger.info(f"Logs dir: {LOGS_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Quantum-Flux Lab API shutting down")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
