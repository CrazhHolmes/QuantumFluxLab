# SynapseScanner Usage Guide v1.3.0

## Quick examples

```bash
# Search for a topic
synapsescanner "quantum entanglement"

# Limit results
synapsescanner "CRISPR" --max-results 5

# Multi-source search (ArXiv + Semantic Scholar + PubMed + bioRxiv)
synapsescanner "neural networks" --sources arxiv,semantic_scholar

# AI-powered summaries (requires Ollama or OpenAI API key)
synapsescanner "graphene" --summarize

# Export to Obsidian
synapsescanner "AI safety" --export-obsidian ~/MyVault
synapsescanner "physics" --md > notes.md

# Export to JSON for piping
synapsescanner "biology" --json | jq '.papers[].title'

# Watch mode (check every 6 hours)
synapsescanner "CRISPR" --watch
synapsescanner "quantum" --watch --notify

# Rabbit hole mode (follow references depth=2)
synapsescanner "time crystals" --depth 2

# Fetch recent papers (no query)
synapsescanner

# Greyscale mode
synapsescanner "neural networks" --noir

# Matrix rain easter egg
synapsescanner "graph theory" --matrix

# Show help
synapsescanner --cheat
```

---

## Three ways to run

### 1. Installed command (recommended)

After `pip install .` from the repo folder:

```bash
synapsescanner "quantum entanglement"
synapsescanner "CRISPR" --max-results 5
synapsescanner --noir
```

### 2. Windows batch file

From the repo folder:

```cmd
cd C:\Users\bings\SynapseScanner
.\synapse.bat "quantum entanglement"
.\synapse.bat "CRISPR" --max-results 5
.\synapse.bat --cheat
```

### 3. Direct Python

```bash
python -m synapsescanner.universal_scanner "quantum entanglement"
python -m synapsescanner.universal_scanner "graph neural networks" --max-results 5
python -m synapsescanner.universal_scanner --noir
```

---

## PowerShell shortcut

The `synapse` function is installed in your PowerShell profile. Usage:

```powershell
synapse "quantum entanglement"
synapse "CRISPR" -MaxResults 5
synapse "neural networks" -Noir
synapse -Cheat
```

---

## All options

| Option | Description |
|--------|-------------|
| `[query]` | Search term (optional, fetches recent papers if omitted) |
| `--max-results N` | Number of papers to fetch (default: 15) |
| `--sources A,B,C` | Comma-separated sources: arxiv, semantic_scholar, pubmed, biorxiv |
| `--fresh` | Bypass cache, fetch fresh results |
| `--summarize` | Enable AI summarization (needs Ollama or OpenAI) |
| `--depth N` | Rabbit hole depth - follow references 0-3 levels deep |
| `--watch` | Watch mode - loop forever (6 hour intervals) |
| `--notify` | Send webhook notification on new papers (with --watch) |
| `--json` | Output JSON instead of formatted UI |
| `--md` | Output Obsidian markdown to stdout |
| `--export-obsidian PATH` | Export papers to Obsidian vault |
| `--noir` | Greyscale mode |
| `--matrix` | Matrix rain easter egg |
| `--cheat` | Show CLI reference |

## Environment variables

| Variable | Effect |
|----------|--------|
| `SYNAPSE_MATRIX=1` | Same as `--matrix` |
| `SYNAPSE_NOIR=1` | Same as `--noir` |
| `OPENAI_API_KEY` | Enable OpenAI summarization backend |
| `SYNAPSE_AI=ollama` | Set default AI provider to Ollama |

## Configuration file

SynapseScanner creates `~/.synapse/config.yaml` on first run:

```yaml
default_sources:
  - arxiv
  - semantic_scholar
max_results: 15
ai_provider: null  # or "ollama" / "openai"
ollama_model: "llama3.2"
webhook_url: null
cache_hours: 24
obsidian_vault: "~/SynapseNotes"
```
