# Changelog

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
