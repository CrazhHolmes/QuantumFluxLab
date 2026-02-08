# Changelog

## [v1.3.0] -- 2026-02-08

### Added
- **Multi-Source Adapter Architecture**: Support for multiple research sources
  - ArXiv (refactored from v1.2.0)
  - Semantic Scholar (new)
  - PubMed/NCBI (new)
  - BioRxiv/MedRxiv (new)
- **SQLite Local Cache**: `~/.synapse/cache.db` speeds up subsequent searches
  - Automatic caching with `--fresh` flag to bypass
  - Configurable cache expiration (default: 24 hours)
- **Knowledge Graph & Cross-References**: 
  - "Hidden Connections" box shows papers linked across sources
  - Detects shared authors, keywords, and title similarities
  - Strength indicator (1-10) for each connection
- **AI Digest Layer** (optional):
  - Ollama support (local LLM, default: llama3.2)
  - OpenAI API support (requires OPENAI_API_KEY)
  - `--summarize` flag enables AI-generated TL;DR and insights
  - Graceful fallback if AI unavailable
- **Export Modules**:
  - `--json`: Structured JSON output for piping
  - `--md`: Obsidian-compatible markdown to stdout
  - `--export-obsidian <path>`: Export to Obsidian vault
- **Watch Mode**: `--watch` loops forever (6-hour intervals)
  - `--notify` triggers webhook on new discoveries
  - Webhook payload includes version, query, new_papers count
- **Configuration System**: `~/.synapse/config.yaml`
  - Default sources, max results, AI provider settings
  - CLI flags override config values
- **Research Rabbit-Holes**: `--depth N` fetches paper references recursively

### Changed
- Enhanced `--cheat` screen with all v1.3.0 options
- Banner now shows v1.3.0
- All 6 CLI aesthetic tricks preserved (gradient, OSC-8, Braille, etc.)

### Technical
- Modular architecture with `sources/`, `exporters/` packages
- Zero mandatory heavy deps (stdlib first)
- Optional deps: pyyaml, ollama, openai
- Full Windows + Unix compatibility

## [v1.2.0] -- 2026-02-02

### Added
- **Search query support**: `synapsescanner "quantum entanglement"` now searches arXiv
- Expanded Contributing section in README with step-by-step guides for adding data sources and patterns
- USAGE.md with comprehensive examples
- PyPI installation instructions in README

### Changed
- Updated `--cheat` output with usage examples
- PowerShell function now supports query argument
- synapse.bat includes helpful comments

## [v1.1.2] -- 2026-02-02

### Fixed
- CI: flake8 alignment-spacing rules (E221, E241, E302, E305) now ignored
- Release workflow: removed unused `id-token` permission that blocked job start

## [v1.1.1] -- 2026-02-02

### Fixed
- Windows cp1252 encoding crash (force UTF-8 stdout)
- Restructured as installable Python package (`pip install .`)

## [v1.1.0] -- 2026-02-02

### Changed
- Rounded-corner discovery box (`╭╮╰╯`)
- Fixed repo URL to `CrazhHolmes/SynapseScanner`
- Complete CLI rewrite: replaced 24 overlapping background features with a clean sequential flow

### Added
- 24-bit true-color gradient banner
- OSC 8 clickable paper hyperlinks in progress bar
- Braille U+2800 sparklines for keyword frequency
- In-place progress bar with cursor hide/show
- Discovery explanation paragraphs after the results box
- `--noir` greyscale mode
- `--matrix` easter egg
- `--cheat` CLI reference
- Deduplicated pattern results

### Removed
- Background animation threads (mascot, floating frame, clock, constellation)
- QR code output
- `tqdm` and `qrcode` dependencies

## [v1.0.0] -- 2026-01-01

### Added
- Initial arXiv scraper with pattern detection
- Cross-disciplinary breakthrough hints (quantum, metamaterial, temporal, AI)
- Whitelist of 20+ open-access research sources
