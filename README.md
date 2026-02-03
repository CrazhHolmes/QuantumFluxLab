# SynapseScanner -- Universal Research Scanner

**Fast, click-through CLI for open-access papers**

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![CI](https://github.com/CrazhHolmes/SynapseScanner/actions/workflows/ci.yml/badge.svg)

---

## What it does

- Scrapes open-access research from **arXiv**, bioRxiv, Zenodo, and 20+ sources
- Detects cross-disciplinary breakthrough patterns (quantum, metamaterials, AI, temporal physics)
- Suggests **concrete, low-cost experiments** with cost estimates
- Displays results with 24-bit true-color gradients, OSC 8 clickable paper links, and Braille sparklines

## Demo

<!-- Captured from a live run against the arXiv API -->
```
  ╭───────────────────────────────────╮
  │       SynapseScanner v1.0.0       │
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

## Quick start

```bash
git clone https://github.com/CrazhHolmes/SynapseScanner.git
cd SynapseScanner
pip install -r synapsescanner/requirements.txt
python synapsescanner/universal_scanner.py
```

Or install as a package:

```bash
pip install .
synapsescanner
```

## CLI flags

| Flag | Effect |
|------|--------|
| `--max-results N` | Papers to fetch (default 15) |
| `--noir` | Greyscale mode |
| `--matrix` | Matrix rain easter egg |
| `--cheat` | Show CLI reference |

Paper URLs in the progress bar are **clickable** in Windows Terminal, iTerm2, and GNOME Terminal (OSC 8 hyperlinks).

## Unique CLI tricks

- **24-bit true-color gradients** -- smooth cyan-to-purple banner (not the 256-color palette)
- **OSC 8 terminal hyperlinks** -- click a paper URL to open it in your browser
- **Braille U+2800 sparklines** -- ultra-compact keyword frequency bars
- **In-place line rewrites** -- flicker-free progress bar
- **Cursor hide/show + atexit** -- clean progress, cursor always restored on crash

## Requirements

- Python 3.9+
- `requests` (the only runtime dependency that isn't stdlib)

```bash
pip install -r synapsescanner/requirements.txt
```

## License

MIT -- fork, hack, cite.
