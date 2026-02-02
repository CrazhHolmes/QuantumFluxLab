#!/usr/bin/env python3
"""
Universal Research Scanner & Reality-Breaker
-------------------------------------------
Scrapes open-access research and suggests concrete, low-cost experiments
to test breakthrough ideas.
"""
import os
import sys
import argparse
import requests
import time
import collections

from cli_extras import (
    show_banner, show_status, show_progress, show_results,
    show_keywords, show_summary, show_cheat, matrix_rain,
    apply_noir, hide_cursor, show_cursor,
)

WHITELIST = [
    "arxiv.org", "biorxiv.org", "chemrxiv.org", "medrxiv.org",
    "osf.io", "zenodo.org", "nasa.gov", "osti.gov", "cern.ch",
    "aip.scitation.org", "aps.org", "iop.org", "pnas.org",
    "nature.com", "science.org", "cell.com", "quantamagazine.org",
    "phys.org", "scitechdaily.com",
]

REPO_URL = "https://github.com/CrazhHolmes/UniversalResearchScanner"


def fetch_recent_papers(domain="arxiv.org", days=7, max_results=10):
    """Fetch recent open-access papers from a domain."""
    papers = []
    if domain == "arxiv.org":
        import xml.etree.ElementTree as ET
        resp = requests.get(
            "https://export.arxiv.org/api/query",
            params={"search_query": "all", "start": 0, "max_results": max_results},
        )
        resp.raise_for_status()
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in ET.fromstring(resp.text).findall("atom:entry", ns):
            papers.append({
                "title":   entry.find("atom:title", ns).text.strip(),
                "summary": entry.find("atom:summary", ns).text.strip(),
                "url":     entry.find("atom:id", ns).text.strip(),
                "domain":  domain,
            })
    return papers


def detect_patterns(papers):
    """Find cross-disciplinary breakthrough hints."""
    patterns = []
    for p in papers:
        txt = (p["title"] + " " + p["summary"]).lower()
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


def build_keyword_counter(papers):
    """Count notable keywords across papers."""
    counter = collections.Counter()
    keywords = [
        "quantum", "entanglement", "superposition", "metamaterial",
        "neural", "AI", "machine learning", "photon", "laser",
        "gravitational", "time crystal", "topology", "spin",
        "lattice", "superconductor", "plasma", "dark matter",
    ]
    for p in papers:
        txt = (p["title"] + " " + p["summary"]).lower()
        for kw in keywords:
            n = txt.count(kw)
            if n:
                counter[kw] += n
    return counter


def main():
    parser = argparse.ArgumentParser(
        description="SynapseScanner - Quantum Research Intelligence",
    )
    parser.add_argument("--matrix", action="store_true",
                        help="Matrix rain easter egg")
    parser.add_argument("--cheat", action="store_true",
                        help="Show CLI reference")
    parser.add_argument("--noir", action="store_true",
                        help="Greyscale mode")
    parser.add_argument("--max-results", type=int, default=15,
                        help="Papers to fetch (default: 15)")
    args = parser.parse_args()

    if args.noir or os.getenv("SYNAPSE_NOIR"):
        apply_noir()

    if args.cheat:
        show_cheat()
        return

    show_banner()

    if args.matrix or os.getenv("SYNAPSE_MATRIX") == "1":
        matrix_rain()

    hide_cursor()
    try:
        # ── Fetch ──
        show_status("Fetching papers from arxiv.org...")
        t0 = time.time()
        papers = fetch_recent_papers("arxiv.org", days=7,
                                     max_results=args.max_results)
        if not papers:
            show_status("No papers returned from API.", "wrn", done=True)
            return
        show_status(f"Found {len(papers)} papers", "ok", done=True)

        # ── Process ──
        for i, paper in enumerate(papers, 1):
            show_progress(paper["url"], i, len(papers))
            time.sleep(0.02)  # smooth the progress bar
        sys.stdout.write("\n")

        # ── Results ──
        patterns = detect_patterns(papers)
        show_results(patterns)

        counter = build_keyword_counter(papers)
        show_keywords(counter)

        unique_patterns = len({p["pattern"] for p in patterns})
        show_summary(len(papers), unique_patterns, time.time() - t0, REPO_URL)

    except requests.RequestException as e:
        show_status(f"Network error: {e}", "err", done=True)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        show_status("Interrupted.", "wrn", done=True)
    finally:
        show_cursor()


if __name__ == "__main__":
    main()
