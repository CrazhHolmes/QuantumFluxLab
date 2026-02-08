# SynapseScanner v1.3.0

**A clean Python CLI that searches open-access research papers and surfaces cross-disciplinary breakthrough patterns.**

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![CI](https://github.com/CrazhHolmes/SynapseScanner/actions/workflows/ci.yml/badge.svg)

**New in v1.3.0**: Multi-source search, AI digest, Knowledge Graph, Obsidian export, Watch mode!

---

## What it does

SynapseScanner fetches recent papers from arXiv (with more sources planned), scans them for cross-disciplinary patterns (quantum, metamaterials, AI, temporal physics), and suggests concrete low-cost experiments you can try at home.

## Demo

<!-- Captured from a live run against the arXiv API -->
```
  ╭───────────────────────────────────╮
  │       SynapseScanner v1.3.0       │
  │   Quantum Research Intelligence   │
  ╰───────────────────────────────────╯

  ✔ Found 15 papers
  arxiv.org/abs/1104.0917v1  ━━━━━━━━━━━━━━━━━━━━━━━━  15/15  100%

  ╭── Discoveries ─────────────────────────────────────────────╮
  │  ⚛  Quantum breakthrough
  │     Test quantum erasure with polarized lenses & laser pointer
  │     ~$30 · Easy
  ╰────────────────────────────────────────────────────────────╯

  ⚛  Quantum breakthrough
    Quantum erasure can be demonstrated with inexpensive optical
    components, opening a low-cost pathway for teaching advanced
    quantum-mechanics experiments in undergraduate labs.

  keywords  entanglement ⣿⣿⣿  topology ⣿⣿⣿

  ✔ Done · 15 papers · 1 patterns · 0.7s
  ⚡ github.com/CrazhHolmes/SynapseScanner
```

## Installation

**From PyPI (when published):**

```bash
pip install synapsescanner
```

**From source:**

```bash
git clone https://github.com/CrazhHolmes/SynapseScanner.git
cd SynapseScanner
pip install .
```

**Or run directly without installing:**

```bash
git clone https://github.com/CrazhHolmes/SynapseScanner.git
cd SynapseScanner
pip install -r synapsescanner/requirements.txt
python -m synapsescanner.universal_scanner "your query"
```

## Quick start

```bash
# Search for a topic
synapsescanner "quantum entanglement"

# Limit results
synapsescanner "CRISPR" --max-results 5

# Fetch recent papers (no query)
synapsescanner

# Greyscale theme
synapsescanner "neural networks" --noir

# Matrix rain easter egg
synapsescanner --matrix

# Show CLI reference card
synapsescanner --cheat
```

## Full usage

### Basic usage

```
synapsescanner [QUERY] [--max-results N] [--noir] [--matrix] [--cheat]
```

| Flag | Effect |
|------|--------|
| `--max-results N` | Number of papers to fetch (default: 15) |
| `--noir` | Greyscale mode -- no color |
| `--matrix` | Matrix rain easter egg before scanning |
| `--cheat` | Print CLI reference card and exit |

### v1.3.0 Features

```bash
# Multi-source search (default: arxiv, semantic_scholar)
synapsescanner "quantum" --sources arxiv,semantic_scholar,pubmed,biorxiv

# AI-powered summaries (requires Ollama or OpenAI API key)
synapsescanner "neural networks" --summarize

# Export to Obsidian markdown
synapsescanner "graphene" --md > notes.md
synapsescanner "AI" --export-obsidian ~/MyVault

# Export to JSON for piping
synapsescanner "physics" --json | jq '.papers[].title'

# Watch mode (check every 6 hours)
synapsescanner "CRISPR" --watch
synapsescanner "quantum" --watch --notify  # with webhook

# Rabbit hole mode (follow references)
synapsescanner "time crystals" --depth 2

# Bypass cache
synapsescanner "new topic" --fresh
```

### Environment variables

| Variable | Equivalent flag | Description |
|----------|----------------|-------------|
| `SYNAPSE_MATRIX=1` | `--matrix` | Enable Matrix-rain easter egg |
| `SYNAPSE_NOIR=1` | `--noir` | Force greyscale colors |
| `OPENAI_API_KEY` | - | Enable OpenAI summarization |
| `SYNAPSE_AI=ollama` | `--summarize` | Default AI provider |

Environment variables and flags can be combined:

```bash
SYNAPSE_NOIR=1 synapsescanner --max-results 7
```

## Output features

- **Clickable paper URLs** -- Click a paper link in the progress bar to open it in your browser (OSC 8 hyperlinks, works in Windows Terminal, iTerm2, GNOME Terminal)
- **Braille sparklines** -- Keyword frequencies rendered as compact `⣀⣄⣤⣦⣶⣷⣿` bars using Unicode Braille patterns (U+2800)
- **True-color gradient banner** -- 24-bit RGB interpolation from cyan to purple (not the 256-color palette)
- **Discovery explanations** -- Each detected pattern includes a short "why it matters" paragraph
- **In-place progress bar** -- Single-line rewrite with cursor hide/show, no scroll spam
- **Crash-safe cursor** -- `atexit` handler guarantees the terminal cursor is restored even on unexpected exit

## Pattern detection

SynapseScanner scans paper titles and abstracts for four cross-disciplinary pattern categories:

| Pattern | Keywords detected | Suggested experiment | Cost |
|---------|------------------|---------------------|------|
| Quantum breakthrough | quantum, entanglement, superposition | Quantum erasure with polarized lenses & laser pointer | ~$30 |
| Metamaterial lens | metamaterial, negative index | Stack microscope slides + oil for negative index demo | ~$20 |
| Temporal periodicity | time crystal, temporal, periodic | 555 timer + LED at 1 Hz | ~$5 |
| AI physics | neural, AI, machine learning | Train tiny model on pendulum data | ~$0 |

## Data sources

**Active in v1.3.0:**

| Source | URL | Status |
|--------|-----|--------|
| arXiv | arxiv.org | ✅ Active -- Atom API |
| Semantic Scholar | semanticscholar.org | ✅ Active -- Graph API |
| PubMed | ncbi.nlm.nih.gov | ✅ Active -- E-utilities |
| bioRxiv/MedRxiv | biorxiv.org | ✅ Active -- Public API |

**In whitelist (planned):**

chemRxiv, OSF, Zenodo, NASA Technical Reports, OSTI, CERN, AIP, APS, IOP, PNAS, Nature, Science, Cell, Quanta Magazine, Phys.org, SciTechDaily

## Windows / PowerShell shortcut

Add this function to your PowerShell `$PROFILE` for a shorter `synapse` command:

```powershell
function synapse {
    param(
        [Parameter(Position=0)][string]$Query,
        [int]$MaxResults = 15,
        [switch]$Matrix,
        [switch]$Noir,
        [switch]$Cheat
    )
    $argsList = @()
    if ($Query) { $argsList += $Query }
    if ($MaxResults -ne 15) { $argsList += "--max-results"; $argsList += $MaxResults }
    if ($Matrix) { $argsList += "--matrix" }
    if ($Noir) { $argsList += "--noir" }
    if ($Cheat) { $argsList += "--cheat" }
    python -m synapsescanner.universal_scanner @argsList
}
```

Then run:

```powershell
synapse "quantum entanglement"           # search
synapse "CRISPR" -MaxResults 5           # limit results
synapse "neural networks" -Noir          # greyscale
synapse -Matrix                          # matrix rain
synapse -Cheat                           # reference card
```

## CMD shortcut (batch file)

Save as `synapse.bat` somewhere on your `PATH`:

```bat
@echo off
python -m synapsescanner.universal_scanner %*
```

Then run:

```cmd
synapse "quantum entanglement"
synapse "CRISPR" --max-results 5
```

## Contributing

We welcome contributions! Here's how to extend SynapseScanner:

### Add a new data source

1. Open `synapsescanner/universal_scanner.py`
2. Add the domain to the `WHITELIST` array:
   ```python
   WHITELIST = [
       "arxiv.org", "biorxiv.org", ...,
       "your-new-source.org",  # add here
   ]
   ```
3. Extend `fetch_recent_papers()` to handle the new domain's API:
   ```python
   def fetch_recent_papers(domain="arxiv.org", query=None, ...):
       ...
       elif domain == "your-new-source.org":
           # Add API fetching logic here
           pass
   ```

### Add a new discovery pattern

1. Open `synapsescanner/universal_scanner.py`
2. Add detection logic in `detect_patterns()`:
   ```python
   if any(kw in txt for kw in ["keyword1", "keyword2"]):
       patterns.append({
           "pattern": "Your Pattern Name",
           "hint": "Suggested experiment description",
           "cost": "~$X", "difficulty": "Easy/Medium/Research",
       })
   ```
3. Open `synapsescanner/cli_extras.py`
4. Add an icon to `_ICONS`:
   ```python
   _ICONS = {
       ...,
       "Your Pattern Name": "🔬",  # pick a Unicode symbol
   }
   ```
5. Add an explanation to `_EXPLANATIONS`:
   ```python
   _EXPLANATIONS = {
       ...,
       "Your Pattern Name": (
           "A paragraph explaining why this pattern matters "
           "and what the suggested experiment demonstrates."
       ),
   }
   ```

### Code style

- Run `flake8 synapsescanner/` before submitting
- Keep functions focused and well-documented
- Test on Windows (for encoding issues) if possible

PRs welcome!

## Requirements

- Python 3.9+
- `requests` (only runtime dependency beyond stdlib)

## License

MIT -- fork, hack, cite.
