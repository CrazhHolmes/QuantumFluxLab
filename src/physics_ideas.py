#!/usr/bin/env python3
"""
Physics Idea Generator
----------------------
Scrapes open-access physics papers and suggests low-cost experiments.
No hardware, no budget claims – just text → ideas.
"""
import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Open-access whitelist
WHITELIST = [
    "arxiv.org",
    "nasa.gov",
    "osti.gov",
    "cern.ch",
    "zenodo.org",
]

def fetch_arxiv(query="piezo corona plasma", max_results=5):
    """Fetches open-access arXiv papers."""
    base = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(base, params=params)
    resp.raise_for_status()
    return resp.text  # Atom feed

def parse_arxiv_atom(atom_text):
    """Parses Atom feed into list of dicts."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(atom_text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        summary = entry.find('atom:summary', ns).text.strip()
        id_url = entry.find('atom:id', ns).text.strip()
        papers.append({
            "title": title,
            "summary": summary,
            "url": id_url,
            "domain": "arxiv.org",
        })
    return papers

def suggest_experiments(papers):
    """Suggests low-cost experiments based on paper content."""
    ideas = []
    for p in papers:
        idea = {
            "title": p["title"],
            "summary": p["summary"][:200] + "…",
            "experiment": "",
            "cost_estimate": "",
            "difficulty": "",
            "url": p["url"],
        }
        # Simple keyword-based suggestions
        if "piezo" in p["summary"].lower():
            idea["experiment"] = "Dead-lighter sparker → 30kV corona plasma"
            idea["cost_estimate"] = "~$20 (piezo sparkers + BBQ lighter)"
            idea["difficulty"] = "Easy"
        elif "infrasound" in p["summary"].lower():
            idea["experiment"] = "TV speaker → 15Hz standing-wave levitation"
            idea["cost_estimate"] = "~$15 (old speakers + Arduino)"
            idea["difficulty"] = "Easy"
        elif "electrostatic" in p["summary"].lower():
            idea["experiment"] = "Cockcroft-Walton → 3kV ion wind"
            idea["cost_estimate"] = "~$25 (multiplier + acrylic)"
            idea["difficulty"] = "Medium"
        else:
            idea["experiment"] = "Literature review + brainstorm"
            idea["cost_estimate"] = "~$0 (time only)"
            idea["difficulty"] = "Research"
        ideas.append(idea)
    return ideas

def main():
    print("🔬 Fetching latest physics papers…")
    atom = fetch_arxiv()
    papers = parse_arxiv_atom(atom)
    ideas = suggest_experiments(papers)
    print("\n💡 Low-Cost Experiment Ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. {idea['title']}")
        print(f"   Summary: {idea['summary']}")
        print(f"   Experiment: {idea['experiment']}")
        print(f"   Cost: {idea['cost_estimate']}")
        print(f"   Difficulty: {idea['difficulty']}")
        print(f"   Paper: {idea['url']}")

if __name__ == "__main__":
    main()
