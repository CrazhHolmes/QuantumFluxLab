# Pusher Promotion Prompt - SynapseScanner v1.3.0

## Release URL
https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0

## Core Message

**SynapseScanner v1.3.0 is live!** 

The Python CLI for research discovery just got a major upgrade:
- 🔍 **Multi-source aggregation**: ArXiv + Semantic Scholar + PubMed + bioRxiv
- 🤖 **AI-powered summaries**: Ollama (local) or OpenAI integration
- 🔗 **Knowledge Graph**: "Hidden Connections" between papers across sources
- 📓 **Obsidian export**: YAML frontmatter + backlinks
- 👁️ **Watch mode**: Background monitoring with webhook notifications
- ⚡ **SQLite cache**: Instant results on repeat queries

## Platform-Specific Posts

### Twitter/X (280 chars)

```
SynapseScanner v1.3.0 is out! 🚀

🔍 Multi-source: ArXiv + Semantic Scholar + PubMed + bioRxiv
🤖 AI summaries (Ollama/OpenAI)
📓 Obsidian export
👁️ Watch mode with webhooks

Python CLI for research discovery—now with a knowledge graph!

https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0
```

### LinkedIn (long-form)

```
Just shipped SynapseScanner v1.3.0 — a major upgrade to my Python CLI for research discovery.

What's new:

🔍 MULTI-SOURCE AGGREGATION
No more bouncing between databases. v1.3.0 searches ArXiv, Semantic Scholar, PubMed, and bioRxiv simultaneously.

🤖 AI-POWERED SUMMARIES
--summarize flag generates TL;DRs + key insights using local Ollama (llama3.2) or OpenAI API.

🔗 KNOWLEDGE GRAPH
"Hidden Connections" box surfaces papers linked across sources—shared authors, keywords, citations.

📓 OBSIDIAN INTEGRATION
Export papers with YAML frontmatter directly to your vault. Backlinks included.

👁️ WATCH MODE
--watch loops every 6 hours, --notify pings webhooks on new discoveries.

⚡ SMART CACHING
SQLite cache means repeat queries are instant.

The CLI still looks gorgeous: 24-bit gradients, OSC-8 clickable URLs, Braille sparklines.

pip install synapsescanner

#OpenScience #CLI #Python #ResearchTools #AcademicTwitter #Obsidian
```

### Reddit (r/coolgithubprojects, r/ObsidianMD, r/commandline)

**Title**: SynapseScanner v1.3.0 — Research CLI with multi-source aggregation, AI summaries, and Obsidian export

```
SynapseScanner is a Python CLI that searches open-access research papers and surfaces cross-disciplinary patterns.

**v1.3.0 Highlights:**

- **Multi-source search**: ArXiv + Semantic Scholar + PubMed + bioRxiv (simultaneous)
- **AI Digest**: --summarize flag with Ollama (local) or OpenAI integration
- **Hidden Connections**: Cross-reference engine finds related papers across sources
- **Obsidian Export**: --md or --export-obsidian with YAML frontmatter
- **Watch Mode**: Background monitoring with webhook notifications
- **SQLite Cache**: Instant results on repeat queries

**The aesthetic is still there:**
- 24-bit cyan→purple gradient banner
- OSC-8 clickable hyperlinks (works in Windows Terminal, iTerm2, GNOME Terminal)
- Braille pattern sparklines (U+2800)
- In-place progress bar with cursor hide/show
- Rounded Unicode boxes (╭╮╰╯)

**Install:**
pip install synapsescanner

**Examples:**
```bash
synapsescanner "quantum" --sources arxiv,semantic_scholar
synapsescanner "CRISPR" --summarize  # needs Ollama running
synapsescanner "AI" --md > notes.md
synapsescanner "graphene" --watch --notify
```

GitHub: https://github.com/CrazhHolmes/SynapseScanner

Would love feedback from researchers and CLI enthusiasts!
```

### dev.to

**Title**: SynapseScanner v1.3.0: The Research CLI Now Has a Knowledge Graph

**Tags**: python, cli, openscience, productivity, academic

```markdown
## What is SynapseScanner?

A Python CLI that searches open-access research papers and suggests low-cost experiments to test breakthrough ideas. Think of it as a research assistant that runs in your terminal.

## What's New in v1.3.0

### 🔍 Multi-Source Aggregation

v1.3.0 expands beyond ArXiv to include:
- **Semantic Scholar** — citation counts, high-quality metadata
- **PubMed** — biomedical literature via E-utilities
- **bioRxiv/medRxiv** — preprints in biology and medicine

```bash
synapsescanner "CRISPR" --sources arxiv,semantic_scholar,pubmed,biorxiv
```

### 🤖 AI-Powered Summaries

The `--summarize` flag generates:
- 2-sentence TL;DR
- 3 key insights
- Suggested tags

Supports **Ollama** (local, default: llama3.2) or **OpenAI API**.

```bash
# Local with Ollama
synapsescanner "quantum" --summarize

# With OpenAI
OPENAI_API_KEY=xxx synapsescanner "neural networks" --summarize
```

### 🔗 Knowledge Graph

The "Hidden Connections" feature finds relationships between papers from different sources—shared authors, keywords, or citation patterns.

### 📓 Obsidian Integration

Export papers directly to your Obsidian vault with proper YAML frontmatter:

```bash
synapsescanner "physics" --export-obsidian ~/MyVault
synapsescanner "biology" --md > notes.md  # stdout
```

### 👁️ Watch Mode

Monitor topics continuously:

```bash
synapsescanner "quantum computing" --watch  # checks every 6 hours
synapsescanner "AI" --watch --notify       # webhook notifications
```

### ⚡ Smart Caching

SQLite cache at `~/.synapse/cache.db` makes repeat queries instant. Use `--fresh` to bypass.

## The CLI Aesthetic

All 6 "rare CLI tricks" from v1.0 are preserved:

1. **24-bit true-color gradients** — cyan to purple interpolation
2. **OSC-8 hyperlinks** — clickable URLs in terminal
3. **Braille sparklines** — U+2800 patterns for keyword frequency
4. **In-place progress** — no scroll spam
5. **Cursor management** — hidden during animation, restored on exit
6. **Rounded Unicode boxes** — ╭╮╰╯ borders

## Installation

```bash
pip install synapsescanner
```

## Configuration

First run creates `~/.synapse/config.yaml`:

```yaml
default_sources:
  - arxiv
  - semantic_scholar
max_results: 15
ai_provider: null  # or "ollama" / "openai"
cache_hours: 24
```

## Links

- GitHub: https://github.com/CrazhHolmes/SynapseScanner
- Release: https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0
- PyPI: https://pypi.org/project/synapsescanner/

---

*Built with Python, requests, and an obsession with terminal UX.*
```

## Image/GIF Suggestions

1. **Demo GIF**: Terminal recording showing the gradient banner, progress bar with clickable URLs, and "Hidden Connections" box
2. **Screenshot**: Side-by-side of regular output vs JSON export
3. **Screenshot**: Obsidian vault with exported papers showing YAML frontmatter

## Hashtags to Use

- Primary: #OpenScience #CLI #Python #ResearchTools
- Secondary: #AcademicTwitter #Obsidian #Productivity #DevTools #AcademicChatter
- Niche: #Bioinformatics #QuantumComputing #MachineLearning
