# SynapseScanner Usage Guide

## Current behavior

SynapseScanner fetches **recent papers from arXiv** and scans them for cross-disciplinary patterns. It does not currently accept a search query — it analyzes whatever recent papers the arXiv API returns.

---

## Running from the repo folder

### Windows CMD

```cmd
cd C:\Users\bings\SynapseScanner
.\synapse.bat
.\synapse.bat --max-results 5
.\synapse.bat --noir
.\synapse.bat --matrix
.\synapse.bat --cheat
```

### PowerShell

```powershell
cd C:\Users\bings\SynapseScanner
.\synapse.bat --max-results 5
.\synapse.bat --noir --matrix
```

### Direct Python (any terminal)

```bash
cd C:\Users\bings\SynapseScanner
python -m synapsescanner.universal_scanner
python -m synapsescanner.universal_scanner --max-results 5
python -m synapsescanner.universal_scanner --noir
python -m synapsescanner.universal_scanner --matrix
python -m synapsescanner.universal_scanner --cheat
```

---

## After installing (`pip install .`)

```bash
synapsescanner
synapsescanner --max-results 10
synapsescanner --noir
synapsescanner --matrix
synapsescanner --cheat
```

---

## PowerShell shortcut function

Add this to your PowerShell profile (`notepad $PROFILE`) for a shorter `synapse` command:

```powershell
function synapse {
    param(
        [int]$MaxResults = 15,
        [switch]$Matrix,
        [switch]$Noir,
        [switch]$Cheat
    )
    $flags = @()
    if ($MaxResults -ne 15) { $flags += "--max-results"; $flags += $MaxResults }
    if ($Matrix) { $flags += "--matrix" }
    if ($Noir) { $flags += "--noir" }
    if ($Cheat) { $flags += "--cheat" }
    python -m synapsescanner.universal_scanner @flags
}
```

Then use:

```powershell
synapse                    # default (15 papers)
synapse -MaxResults 5      # quick scan
synapse -Matrix            # matrix rain easter egg
synapse -Noir              # greyscale mode
synapse -Cheat             # CLI reference card
```

---

## Available flags

| Flag | Effect |
|------|--------|
| `--max-results N` | Number of papers to fetch (default: 15) |
| `--noir` | Greyscale mode |
| `--matrix` | Matrix rain easter egg |
| `--cheat` | Show CLI reference card |

## Environment variables

| Variable | Effect |
|----------|--------|
| `SYNAPSE_MATRIX=1` | Same as `--matrix` |
| `SYNAPSE_NOIR=1` | Same as `--noir` |

---

## Note on search queries

The current version does **not** support search queries. It fetches recent papers from arXiv's "all" category. Query-based search is planned for a future release.
