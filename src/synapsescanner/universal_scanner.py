#!/usr/bin/env python3
"""
Universal Research Scanner & Reality-Breaker v1.3.0
---------------------------------------------------
Multi-source research scanner with AI digest, knowledge graph,
Obsidian export, and watch mode.
"""
import os
import sys
import argparse
import time
import json
from typing import List, Optional

# Ensure our src directory is in path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from synapsescanner.cli_extras import (
    show_banner, show_status, show_progress, show_results,
    show_keywords, show_summary, show_cheat, matrix_rain,
    apply_noir, hide_cursor, show_cursor,
    show_connections, show_ai_digest, notify_webhook,
)

# Import new modules (with graceful fallback)
try:
    from synapsescanner.sources import Paper, get_source, list_sources, SOURCE_REGISTRY
    from synapsescanner.cache import get_cache
    from synapscescanner.config import get_config
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from synapsescanner.crossref import find_connections
    CROSSREF_AVAILABLE = True
except ImportError:
    CROSSREF_AVAILABLE = False

try:
    from synapsescanner.ai import AISummarizer, summarize_abstract
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from synapsescanner.exporters.obsidian import ObsidianExporter
    from synapsescanner.exporters.json import JSONExporter
    EXPORTERS_AVAILABLE = True
except ImportError:
    EXPORTERS_AVAILABLE = False

REPO_URL = "https://github.com/CrazhHolmes/SynapseScanner"
VERSION = "1.3.0"


def fetch_from_sources(query: str, sources: List[str], limit: int, 
                       use_cache: bool = True) -> List[Paper]:
    """Fetch papers from multiple sources.
    
    Args:
        query: Search query
        sources: List of source names
        limit: Max results per source
        use_cache: Whether to use cache
        
    Returns:
        List of Paper objects
    """
    all_papers = []
    
    for source_name in sources:
        source = get_source(source_name)
        if not source:
            show_status(f"Unknown source: {source_name}", "wrn", done=True)
            continue
        
        # Check cache first
        if use_cache and CACHE_AVAILABLE:
            cache = get_cache()
            cached = cache.get_cached(query, source_name)
            if cached:
                show_status(f"Using cached {source_name} results", "ok", done=True)
                all_papers.extend(cached)
                continue
        
        show_status(f"Searching {source_name}...", "info")
        
        try:
            papers = source.search(query, limit=limit)
            
            if use_cache and CACHE_AVAILABLE:
                cache = get_cache()
                cache.save_papers(papers)
                cache.record_query(query, source_name, limit, len(papers))
            
            all_papers.extend(papers)
            show_status(f"Found {len(papers)} papers from {source_name}", "ok", done=True)
            
        except Exception as e:
            show_status(f"{source_name} error: {str(e)[:40]}", "err", done=True)
    
    return all_papers


def fetch_references_recursive(papers: List[Paper], depth: int, 
                               max_per_paper: int = 5) -> List[Paper]:
    """Fetch references recursively (rabbit hole mode).
    
    Args:
        papers: Initial papers
        depth: How many levels deep to go
        max_per_paper: Max references to fetch per paper
        
    Returns:
        Combined list of original and referenced papers
    """
    if depth <= 0:
        return papers
    
    all_papers = list(papers)
    seen_ids = {(p.id, p.source) for p in papers}
    
    for level in range(depth):
        show_status(f"Digging deeper... level {level + 1}/{depth}", "info")
        
        new_papers = []
        for paper in papers:
            source = get_source(paper.source)
            if not source:
                continue
            
            try:
                refs = source.fetch_references(paper)
                for ref in refs[:max_per_paper]:
                    key = (ref.id, ref.source)
                    if key not in seen_ids:
                        seen_ids.add(key)
                        new_papers.append(ref)
            except Exception:
                pass
        
        if not new_papers:
            break
        
        all_papers.extend(new_papers)
        papers = new_papers
        
        show_status(f"Level {level + 1}: Found {len(new_papers)} more papers", "ok", done=True)
    
    return all_papers


def detect_patterns(papers: List[Paper]):
    """Find cross-disciplinary breakthrough hints."""
    patterns = []
    
    for paper in papers:
        txt = (paper.title + " " + paper.abstract).lower()
        
        if any(q in txt for q in ["quantum", "entanglement", "superposition"]):
            patterns.append({
                "pattern": "Quantum breakthrough",
                "hint": "Test quantum erasure with polarized lenses & laser pointer",
                "cost": "~$30", "difficulty": "Easy",
            })
        if any(m in txt for m in ["metamaterial", "negative index"]):
            patterns.append({
                "pattern": "Metamaterial lens",
                "hint": "Stack microscope slides + oil for negative index demo",
                "cost": "~$20", "difficulty": "Easy",
            })
        if any(t in txt for t in ["time crystal", "temporal", "periodic"]):
            patterns.append({
                "pattern": "Temporal periodicity",
                "hint": "555 timer + LED at 1 Hz, observe after-image",
                "cost": "~$5", "difficulty": "Easy",
            })
        if any(a in txt for a in ["neural", "AI", "machine learning"]):
            patterns.append({
                "pattern": "AI physics",
                "hint": "Train tiny model on physics data, predict pendulum motion",
                "cost": "~$0 (laptop)", "difficulty": "Research",
            })
    
    return patterns


def build_keyword_counter(papers: List[Paper]):
    """Count notable keywords across papers."""
    import collections
    counter = collections.Counter()
    keywords = [
        "quantum", "entanglement", "superposition", "metamaterial",
        "neural", "AI", "machine learning", "photon", "laser",
        "gravitational", "time crystal", "topology", "spin",
        "lattice", "superconductor", "plasma", "dark matter",
    ]
    
    for paper in papers:
        txt = (paper.title + " " + paper.abstract).lower()
        for kw in keywords:
            n = txt.count(kw)
            if n:
                counter[kw] += n
    
    return counter


def watch_mode(args, config):
    """Run in watch mode (daemon-like loop)."""
    import time
    from datetime import datetime
    
    sleep_hours = 6
    show_status(f"Watch mode active. Checking every {sleep_hours} hours.", "info", done=True)
    show_status("Press Ctrl+C to stop", "info", done=True)
    
    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            show_status(f"[{now}] Scanning...", "info")
            
            # Run scan
            new_papers = run_scan(args, config, silent=True)
            
            if new_papers and args.notify:
                # Send webhook notification
                webhook_url = config.webhook_url if config else None
                if webhook_url:
                    top_paper = new_papers[0].title if new_papers else "N/A"
                    payload = {
                        "version": VERSION,
                        "query": args.query or "(recent)",
                        "new_papers": len(new_papers),
                        "top_discovery": top_paper,
                        "timestamp": now
                    }
                    if notify_webhook(webhook_url, payload):
                        show_status(f"Notification sent: {len(new_papers)} new papers", "ok", done=True)
            
            # Sleep
            for _ in range(sleep_hours * 3600):
                time.sleep(1)
                
    except KeyboardInterrupt:
        show_status("Watch mode stopped.", "wrn", done=True)


def run_scan(args, config, silent: bool = False) -> List[Paper]:
    """Run a single scan.
    
    Args:
        args: Command line arguments
        config: Configuration object
        silent: If True, suppress UI output
        
    Returns:
        List of papers found
    """
    # Determine sources
    if args.sources:
        sources = args.sources.split(",")
    elif config:
        sources = config.default_sources
    else:
        sources = ["arxiv"]
    
    # Determine limit
    limit = args.max_results or (config.max_results if config else 15)
    
    # Determine query
    query = args.query or ""
    
    # Check cache availability
    use_cache = not args.fresh and CACHE_AVAILABLE
    
    # Fetch papers
    papers = fetch_from_sources(query, sources, limit, use_cache)
    
    # Rabbit hole mode
    if args.depth and args.depth > 0:
        papers = fetch_references_recursive(papers, args.depth)
    
    return papers


def main():
    parser = argparse.ArgumentParser(
        description="SynapseScanner v1.3.0 - Universal Research Intelligence",
    )
    parser.add_argument("query", nargs="?", default=None,
                        help="Search query (optional)")
    parser.add_argument("--matrix", action="store_true",
                        help="Matrix rain easter egg")
    parser.add_argument("--cheat", action="store_true",
                        help="Show CLI reference")
    parser.add_argument("--noir", action="store_true",
                        help="Greyscale mode")
    parser.add_argument("--max-results", type=int, default=None,
                        help="Papers to fetch (default: 15)")
    
    # New v1.3.0 arguments
    parser.add_argument("--sources", type=str, default=None,
                        help="Comma-separated sources (arxiv,semantic_scholar,pubmed,biorxiv)")
    parser.add_argument("--fresh", action="store_true",
                        help="Bypass cache")
    parser.add_argument("--summarize", action="store_true",
                        help="Enable AI summarization")
    parser.add_argument("--depth", type=int, default=0,
                        help="Rabbit hole depth (0-3, default: 0)")
    parser.add_argument("--watch", action="store_true",
                        help="Watch mode (loop forever)")
    parser.add_argument("--notify", action="store_true",
                        help="Send webhook notifications (with --watch)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of UI")
    parser.add_argument("--md", action="store_true",
                        help="Output Obsidian markdown to stdout")
    parser.add_argument("--export-obsidian", type=str, default=None,
                        help="Export to Obsidian vault path")
    
    args = parser.parse_args()
    
    # Load config
    config = get_config() if CACHE_AVAILABLE else None
    
    # Apply noir mode
    if args.noir or os.getenv("SYNAPSE_NOIR"):
        apply_noir()
    
    # Show cheat sheet
    if args.cheat:
        show_cheat()
        return
    
    # Matrix rain easter egg
    if args.matrix or os.getenv("SYNAPSE_MATRIX") == "1":
        matrix_rain()
    
    # Watch mode
    if args.watch:
        watch_mode(args, config)
        return
    
    # Normal scan mode
    hide_cursor()
    try:
        t0 = time.time()
        
        # Show banner (unless JSON/MD mode)
        if not args.json and not args.md:
            show_banner()
        
        # Run the scan
        papers = run_scan(args, config, silent=args.json or args.md)
        
        if not papers:
            if not args.json and not args.md:
                show_status("No papers found.", "wrn", done=True)
            return
        
        # Find connections
        connections = []
        if CROSSREF_AVAILABLE and len(papers) > 1:
            connections = find_connections(papers)
        
        # AI Summarization
        ai_summaries = []
        if args.summarize and AI_AVAILABLE and not args.json and not args.md:
            show_status("Generating AI summaries...", "info")
            summarizer = AISummarizer()
            
            for i, paper in enumerate(papers[:3]):  # Summarize top 3
                summary = summarizer.summarize(paper.abstract, paper.title)
                if summary:
                    ai_summaries.append(summary)
            
            if ai_summaries:
                show_status(f"Generated {len(ai_summaries)} summaries", "ok", done=True)
        
        # JSON output mode
        if args.json and EXPORTERS_AVAILABLE:
            exporter = JSONExporter()
            output = exporter.export(papers, connections)
            print(output)
            return
        
        # Markdown output mode
        if args.md and EXPORTERS_AVAILABLE:
            exporter = ObsidianExporter()
            output = exporter.export_to_string(papers, connections, args.query or "")
            print(output)
            return
        
        # Obsidian export
        if args.export_obsidian and EXPORTERS_AVAILABLE:
            exporter = ObsidianExporter(args.export_obsidian)
            result = exporter.export(papers, connections, args.query or "")
            show_status(result, "ok", done=True)
        
        # Standard UI output
        # Progress display
        for i, paper in enumerate(papers, 1):
            show_progress(paper.url, i, len(papers))
            time.sleep(0.02)
        sys.stdout.write("\n")
        
        # Detect patterns
        patterns = detect_patterns(papers)
        show_results(patterns)
        
        # Show connections
        if connections and not args.json and not args.md:
            show_connections(connections)
        
        # Show AI digests
        if ai_summaries and not args.json and not args.md:
            for summary in ai_summaries:
                show_ai_digest({
                    "tldr": summary.tldr,
                    "insights": summary.insights,
                    "tags": summary.tags
                })
        
        # Show keywords
        counter = build_keyword_counter(papers)
        show_keywords(counter)
        
        # Summary
        unique_patterns = len({p["pattern"] for p in patterns})
        show_summary(len(papers), unique_patterns, time.time() - t0, REPO_URL)
        
    except Exception as e:
        if not args.json and not args.md:
            show_status(f"Error: {e}", "err", done=True)
        else:
            # JSON error output
            print(json.dumps({"error": str(e)}))
    except KeyboardInterrupt:
        if not args.json and not args.md:
            sys.stdout.write("\n")
            show_status("Interrupted.", "wrn", done=True)
    finally:
        show_cursor()


if __name__ == "__main__":
    main()
