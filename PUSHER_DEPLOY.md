# SynapseScanner v1.3.0 - Pusher Deployment Ready

## 🚀 ONE-LINER (Twitter/X)

```
SynapseScanner v1.3.0 🚀 Multi-source research CLI (ArXiv + Semantic Scholar + PubMed + bioRxiv) with AI summaries, Obsidian export, and knowledge graph connections. Python • Clickable URLs • Braille sparklines. https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0
```

---

## 🧵 TWITTER THREAD (5 tweets)

**Tweet 1:**
```
🚀 SynapseScanner v1.3.0 is live!

🔍 Multi-source: ArXiv + Semantic Scholar + PubMed + bioRxiv
🤖 AI summaries via Ollama/OpenAI
📓 Obsidian export
👁️ Watch mode w/ webhooks

The Python CLI for research just got a knowledge graph!

👇 Thread
```

**Tweet 2:**
```
What's new in v1.3.0?

The "Hidden Connections" feature finds papers linked across sources—same authors, keywords, citations.

Cross-source discovery without the tab hell.
```

**Tweet 3:**
```
The AI Digest feature (--summarize) generates:

• 2-sentence TL;DR
• 3 key insights
• Suggested tags

Works with local Ollama (llama3.2) or OpenAI API.

Privacy-first option: never leaves your machine.
```

**Tweet 4:**
```
Obsidian users: --export-obsidian dumps papers with YAML frontmatter directly to your vault.

Backlinks included. Research → Notes in one command.

synapsescanner "quantum" --export-obsidian ~/MyVault
```

**Tweet 5:**
```
And yes, the CLI still looks gorgeous:

• 24-bit cyan→purple gradients
• OSC-8 clickable hyperlinks
• Braille sparklines (U+2800)
• In-place progress bars
• Rounded Unicode boxes

pip install synapsescanner

https://github.com/CrazhHolmes/SynapseScanner
```

---

## 💼 LINKEDIN POST

```
Just shipped SynapseScanner v1.3.0 — a major upgrade to my Python CLI for research discovery.

WHAT IT DOES
SynapseScanner searches open-access research papers across multiple sources and surfaces cross-disciplinary breakthrough patterns.

WHAT'S NEW IN V1.3.0

🔍 MULTI-SOURCE AGGREGATION
No more bouncing between databases. v1.3.0 searches ArXiv, Semantic Scholar, PubMed, and bioRxiv simultaneously.

🤖 AI-POWERED SUMMARIES
The --summarize flag generates TL;DRs + key insights using local Ollama (llama3.2) or OpenAI API. Privacy-first: runs entirely locally if you want.

🔗 KNOWLEDGE GRAPH
"Hidden Connections" box shows papers linked across sources—shared authors, keywords, citations. Strength indicator (1-10) for each connection.

📓 OBSIDIAN INTEGRATION
Export papers with YAML frontmatter directly to your vault. Backlinks included.

👁️ WATCH MODE
--watch loops every 6 hours, --notify triggers webhooks on new discoveries. Set it and forget it.

⚡ SMART CACHING
SQLite cache means repeat queries are instant.

THE AESTHETIC
All 6 "rare CLI tricks" preserved:
• 24-bit true-color gradient banner
• OSC-8 clickable hyperlinks
• Braille U+2800 sparklines
• In-place progress with cursor hide/show
• Rounded Unicode boxes (╭╮╰╯)

GET IT
pip install synapsescanner

GitHub: https://github.com/CrazhHolmes/SynapseScanner
Release: https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0

#OpenScience #CLI #Python #ResearchTools #Productivity #AcademicTwitter #Obsidian
```

---

## 👾 REDDIT (r/coolgithubprojects)

**Title:** SynapseScanner v1.3.0 — Research CLI with multi-source aggregation, AI summaries, and Obsidian export

```
SynapseScanner is a Python CLI that searches open-access research papers across multiple sources and surfaces cross-disciplinary patterns.

V1.3.0 HIGHLIGHTS

Multi-source search:
• ArXiv (Atom API)
• Semantic Scholar (Graph API)
• PubMed (E-utilities)
• bioRxiv/MedRxiv (Public API)

AI Digest (--summarize):
• 2-sentence TL;DR
• 3 key insights
• Suggested tags
• Local via Ollama or OpenAI API

Hidden Connections:
Finds papers linked across sources—shared authors, keywords, citations. Shows strength (1-10).

Obsidian Export:
--md or --export-obsidian with YAML frontmatter and backlinks.

Watch Mode:
--watch monitors every 6 hours, --notify pings webhooks on new papers.

JSON Export:
--json for piping into other tools.

THE AESTHETIC
24-bit gradients, OSC-8 clickable URLs, Braille sparklines (U+2800), in-place progress bars, rounded Unicode boxes.

INSTALL
pip install synapsescanner

EXAMPLES
synapsescanner "quantum" --sources arxiv,semantic_scholar
synapsescanner "CRISPR" --summarize  # needs Ollama
synapsescanner "AI" --md > notes.md
synapsescanner "graphene" --watch --notify

LINKS
GitHub: https://github.com/CrazhHolmes/SynapseScanner
Release: https://github.com/CrazhHolmes/SynapseScanner/releases/tag/v1.3.0
```

---

## 📊 DEV.TO POST

**Title:** SynapseScanner v1.3.0: The Research CLI Now Has a Knowledge Graph
**Tags:** python, cli, openscience, productivity, academic

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

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Twitter/X thread posted
- [ ] LinkedIn post published
- [ ] Reddit post submitted
- [ ] Dev.to article published
- [ ] GitHub Release notes updated
- [ ] PyPI description updated (if needed)

---

## 📸 SCREENSHOT COMMANDS (for media)

```bash
# Demo the gradient banner + progress bar
synapsescanner "quantum" --max-results 3

# Demo multi-source
synapsescanner "neural networks" --sources arxiv,semantic_scholar --max-results 5

# Demo JSON output
synapsescanner "AI" --json --max-results 3

# Demo Obsidian markdown
synapsescanner "graphene" --md --max-results 2
```

---

**Ready to copy/paste!** 🚀
