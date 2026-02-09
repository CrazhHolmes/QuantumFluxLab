# src/cli_extras.py
"""
Clean CLI UX for SynapseScanner.

Tricks used (most are rarely seen in Python CLI tools):
  - 24-bit true-color ANSI gradients (not 256-color)
  - OSC 8 clickable hyperlinks — paper URLs open in your browser
  - Braille-pattern U+2800 sparklines for keyword frequency
  - In-place single-line rewrites for flicker-free progress
  - Cursor hide/show so the blinking caret doesn't fight the bar
  - atexit guard so cursor always comes back, even on crash
"""
import sys
import os
import atexit
import shutil
import time
import random

# ── Enable ANSI escapes and UTF-8 output on Windows ──
if os.name == "nt":
    os.system("")                           # enable VT processing
    sys.stdout.reconfigure(encoding="utf-8")  # box-drawing & braille need UTF-8

# ── ANSI primitives ──
RESET    = "\033[0m"
BOLD     = "\033[1m"
DIM      = "\033[2m"
ITALIC   = "\033[3m"
HIDE_CUR = "\033[?25l"
SHOW_CUR = "\033[?25h"
CLR_LINE = "\033[2K"


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _hyperlink(url, label):
    """OSC 8 — makes *label* a clickable link in Windows Terminal,
    iTerm2, GNOME Terminal, and most modern emulators."""
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


# ── Colour theme ──
class _Theme:
    c1  = (0, 210, 255)       # cyan
    c2  = (140, 80, 255)      # purple
    ok  = (0, 220, 140)       # green
    err = (255, 70, 70)       # red
    wrn = (255, 200, 50)      # amber
    dim = (100, 100, 120)     # muted grey

THEME = _Theme()


def apply_noir():
    THEME.c1  = (210, 210, 210)
    THEME.c2  = (140, 140, 140)
    THEME.ok  = (190, 190, 190)
    THEME.err = (170, 170, 170)
    THEME.wrn = (160, 160, 160)
    THEME.dim = (100, 100, 100)


# ── Cursor safety ──
def hide_cursor():
    sys.stdout.write(HIDE_CUR)
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write(SHOW_CUR)
    sys.stdout.flush()

atexit.register(show_cursor)


# ── Banner (true-color gradient box, rounded corners) ──
def show_banner():
    cols = shutil.get_terminal_size().columns
    title    = "SynapseScanner v1.4.0"
    subtitle = "Quantum Research Intelligence"
    inner = max(len(title), len(subtitle)) + 6
    pad = " " * max(0, (cols - inner - 2) // 2)

    def _grad(left, fill, right, w):
        chars = left + fill * w + right
        out = ""
        for i, ch in enumerate(chars):
            t = i / max(len(chars) - 1, 1)
            r, g, b = _lerp(THEME.c1, THEME.c2, t)
            out += rgb(r, g, b) + ch
        return out + RESET

    def _row(text, style=""):
        gap = inner - len(text)
        lp, rp = gap // 2, gap - gap // 2
        return (rgb(*THEME.c1) + "│" + RESET + style
                + " " * lp + text + " " * rp
                + RESET + rgb(*THEME.c2) + "│" + RESET)

    sys.stdout.write(
        f"\n{pad}{_grad('╭', '─', '╮', inner)}\n"
        f"{pad}{_row(title, BOLD)}\n"
        f"{pad}{_row(subtitle, DIM)}\n"
        f"{pad}{_grad('╰', '─', '╯', inner)}\n\n"
    )
    sys.stdout.flush()


# ── Status line ──
def show_status(msg, style="info", done=False):
    """Print / overwrite a status line.
    done=False  → stays on current line (no newline).
    done=True   → clears current line first, then prints with newline."""
    colours = {"info": THEME.c1, "ok": THEME.ok, "err": THEME.err, "wrn": THEME.wrn}
    icons   = {"info": "◌", "ok": "✔", "err": "✘", "wrn": "▲"}
    c   = colours.get(style, THEME.dim)
    sym = icons.get(style, "●")
    pre = f"\r{CLR_LINE}" if done else ""
    end = "\n" if done else ""
    sys.stdout.write(f"{pre}  {rgb(*c)}{sym}{RESET} {msg}{end}")
    sys.stdout.flush()


# ── Progress bar (in-place rewrite, clickable URL) ──
def show_progress(url, current, total):
    display = url.replace("http://", "").replace("https://", "")
    if len(display) > 30:
        display = display[:27] + "..."
    link = _hyperlink(url, display)

    bar_w  = 24
    ratio  = current / total if total else 0
    filled = round(ratio * bar_w)
    bar    = (rgb(*THEME.c1) + "━" * filled
              + rgb(*THEME.dim) + "─" * (bar_w - filled) + RESET)

    pct = f"{int(ratio * 100):>3}%"
    cnt = f"{current}/{total}"
    sys.stdout.write(f"{CLR_LINE}\r  {link}  {bar}  {DIM}{cnt}  {pct}{RESET}")
    sys.stdout.flush()


# ── Results box (deduplicated, Unicode borders) ──
_ICONS = {
    "Quantum breakthrough": "⚛",
    "Metamaterial lens":    "◈",
    "Temporal periodicity": "◎",
    "AI physics":           "◆",
}

_EXPLANATIONS = {
    "Quantum breakthrough": (
        "Quantum erasure can be demonstrated with inexpensive optical"
        " components, opening a low-cost pathway for teaching advanced"
        " quantum-mechanics experiments in undergraduate labs."
    ),
    "Metamaterial lens": (
        "Stacking everyday glass slides with index-matching oil recreates"
        " the negative-refraction effect normally seen only in engineered"
        " nanostructures, making metamaterial optics accessible on a bench."
    ),
    "Temporal periodicity": (
        "A simple 555-timer circuit can produce the same discrete time-"
        "symmetry breaking that underpins time-crystal research, giving"
        " students a hands-on analogy for cutting-edge condensed-matter physics."
    ),
    "AI physics": (
        "Training a small neural network on pendulum data shows how machine"
        " learning can rediscover Newtonian mechanics from raw observations,"
        " illustrating physics-informed ML with zero hardware cost."
    ),
}

def show_results(patterns):
    seen, unique = set(), []
    for p in patterns:
        if p["pattern"] not in seen:
            seen.add(p["pattern"])
            unique.append(p)

    if not unique:
        show_status("No breakthrough patterns detected.", "wrn", done=True)
        return

    cols = shutil.get_terminal_size().columns
    w = min(62, cols - 4)
    br, bg, bb = _lerp(THEME.c1, THEME.c2, 0.25)
    bdr = rgb(br, bg, bb)

    hdr   = " Discoveries "
    hline = "─" * 2 + hdr + "─" * max(0, w - 4 - len(hdr))

    lines = [f"\n  {bdr}╭{hline}╮{RESET}"]
    for p in unique:
        icon = _ICONS.get(p["pattern"], "●")
        lines.append(f"  {bdr}│{RESET}  {BOLD}{icon}  {p['pattern']}{RESET}")
        lines.append(f"  {bdr}│{RESET}     {DIM}{p['hint']}{RESET}")
        lines.append(f"  {bdr}│{RESET}     {DIM}{p['cost']} · {p['difficulty']}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
    lines.append(f"  {bdr}╰{'─' * (w - 2)}╯{RESET}")

    sys.stdout.write("\n".join(lines) + "\n")

    # Explanation paragraph for each discovery
    for p in unique:
        explanation = _EXPLANATIONS.get(p["pattern"])
        if explanation:
            icon = _ICONS.get(p["pattern"], "●")
            sys.stdout.write(f"\n  {BOLD}{icon}  {p['pattern']}{RESET}\n")
            # Word-wrap the explanation to fit the terminal
            max_w = min(cols - 6, 72)
            words = explanation.split()
            line = "  "
            for word in words:
                if len(line) + len(word) + 1 > max_w:
                    sys.stdout.write(f"  {DIM}{line}{RESET}\n")
                    line = "  "
                line += (" " if len(line) > 2 else "") + word
            if line.strip():
                sys.stdout.write(f"  {DIM}{line}{RESET}\n")

    sys.stdout.flush()


# ── Keywords (braille-dot sparklines) ──
def show_keywords(counter, limit=6):
    if not counter:
        return
    braille = " ⣀⣄⣤⣦⣶⣷⣿"
    peak  = max(counter.values())
    items = sorted(counter.items(), key=lambda x: -x[1])[:limit]

    sys.stdout.write(f"\n  {DIM}keywords{RESET}  ")
    for word, freq in items:
        t = freq / peak
        r, g, b = _lerp(THEME.c1, THEME.c2, t)
        lvl = max(1, int(t * (len(braille) - 1)))
        sys.stdout.write(f"{rgb(r, g, b)}{word}{RESET} {DIM}{braille[lvl] * 3}{RESET}  ")
    sys.stdout.write("\n")
    sys.stdout.flush()


# ── Summary (one-liner with clickable repo link) ──
def show_summary(papers, patterns, elapsed, repo_url=None):
    r, g, b = THEME.ok
    sys.stdout.write(
        f"\n  {rgb(r, g, b)}✔{RESET} {BOLD}Done{RESET}"
        f" {DIM}·{RESET} {papers} papers"
        f" {DIM}·{RESET} {patterns} patterns"
        f" {DIM}·{RESET} {elapsed:.1f}s\n"
    )
    if repo_url:
        link = _hyperlink(repo_url, repo_url.replace("https://", ""))
        sys.stdout.write(f"  {DIM}⚡{RESET} {link}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()


# ── Hidden Connections box (rounded corners) ──
def show_connections(connections):
    """Display hidden connections between papers."""
    if not connections:
        return
    
    cols = shutil.get_terminal_size().columns
    w = min(62, cols - 4)
    br, bg, bb = _lerp(THEME.c1, THEME.c2, 0.25)
    bdr = rgb(br, bg, bb)
    
    hdr = " Hidden Connections "
    hline = "─" * 2 + hdr + "─" * max(0, w - 4 - len(hdr))
    
    lines = [f"\n  {bdr}╭{hline}╮{RESET}"]
    
    for conn in connections[:5]:  # Show top 5
        icon = "🔗" if conn.strength >= 7 else "~"
        lines.append(f"  {bdr}│{RESET}  {icon}  {conn.paper_a.source} ↔ {conn.paper_b.source}")
        lines.append(f"  {bdr}│{RESET}     {DIM}{conn.reason[:50]}...{RESET}" if len(conn.reason) > 50 
                     else f"  {bdr}│{RESET}     {DIM}{conn.reason}{RESET}")
        # Strength indicator
        stars = "★" * (conn.strength // 2)
        lines.append(f"  {bdr}│{RESET}     {rgb(*THEME.ok)}{stars}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
    
    lines.append(f"  {bdr}╰{'─' * (w - 2)}╯{RESET}")
    
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


# ── AI Digest box ──
def show_ai_digest(summary):
    """Display AI-generated summary in a rounded box.
    
    Args:
        summary: Dict with 'tldr', 'insights', 'tags'
    """
    if not summary:
        return
    
    cols = shutil.get_terminal_size().columns
    w = min(62, cols - 4)
    br, bg, bb = _lerp(THEME.c1, THEME.c2, 0.75)  # Different gradient position
    bdr = rgb(br, bg, bb)
    
    hdr = " AI Digest "
    hline = "─" * 2 + hdr + "─" * max(0, w - 4 - len(hdr))
    
    lines = [f"\n  {bdr}╭{hline}╮{RESET}"]
    
    # TL;DR
    tldr = summary.get("tldr", "")
    if tldr:
        lines.append(f"  {bdr}│{RESET}  {BOLD}💡 TL;DR{RESET}")
        # Word wrap TL;DR
        words = tldr.split()
        line_text = ""
        for word in words:
            if len(line_text) + len(word) + 1 > w - 6:
                lines.append(f"  {bdr}│{RESET}     {DIM}{line_text}{RESET}")
                line_text = word
            else:
                line_text += (" " if line_text else "") + word
        if line_text:
            lines.append(f"  {bdr}│{RESET}     {DIM}{line_text}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
    
    # Insights
    insights = summary.get("insights", [])
    if insights:
        lines.append(f"  {bdr}│{RESET}  {BOLD}🔍 Key Insights{RESET}")
        for insight in insights[:3]:
            # Truncate if too long
            display = insight[:w-8] + "..." if len(insight) > w-8 else insight
            lines.append(f"  {bdr}│{RESET}     {DIM}• {display}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
    
    # Tags
    tags = summary.get("tags", [])
    if tags:
        tag_str = " ".join(f"#{t}" for t in tags[:5])
        lines.append(f"  {bdr}│{RESET}  {BOLD}🏷️  Tags{RESET} {rgb(*THEME.c2)}{tag_str}{RESET}")
    
    lines.append(f"  {bdr}╰{'─' * (w - 2)}╯{RESET}")
    
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


# ── Webhook notification ──
def notify_webhook(url: str, payload: dict) -> bool:
    """Send notification webhook.
    
    Args:
        url: Webhook URL
        payload: JSON payload
        
    Returns:
        True if successful
    """
    try:
        import requests
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code < 400
    except Exception:
        return False


# ── Breakthrough Preview (v1.4.0 AutoDocs) ──
def show_breakthrough_preview(doc_path: str):
    """Show preview of generated breakthrough documentation.
    
    Args:
        doc_path: Path to the generated markdown file
    """
    from pathlib import Path
    
    try:
        content = Path(doc_path).read_text(encoding='utf-8')
        # Extract title
        title = "Breakthrough Documentation"
        for line in content.split('\n')[:5]:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        cols = shutil.get_terminal_size().columns
        w = min(62, cols - 4)
        br, bg, bb = _lerp(THEME.c1, THEME.c2, 0.5)
        bdr = rgb(br, bg, bb)
        
        hdr = " AutoDocs Generated "
        hline = "─" * 2 + hdr + "─" * max(0, w - 4 - len(hdr))
        
        lines = [f"\n  {bdr}╭{hline}╮{RESET}"]
        lines.append(f"  {bdr}│{RESET}  {BOLD}📝 {title[:50]}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
        lines.append(f"  {bdr}│{RESET}  {DIM}Saved to:{RESET}")
        lines.append(f"  {bdr}│{RESET}  {rgb(*THEME.c2)}{doc_path}{RESET}")
        lines.append(f"  {bdr}│{RESET}")
        lines.append(f"  {bdr}│{RESET}  {DIM}Files generated:{RESET}")
        
        # Check for related files
        doc_dir = Path(doc_path).parent
        doc_name = Path(doc_path).stem
        
        files_to_check = [
            ("README.md", "Updated"),
            ("docs/BREAKTHROUGHS.md", "Log entry added"),
        ]
        
        for filename, status in files_to_check:
            filepath = doc_dir / filename
            if filepath.exists():
                lines.append(f"  {bdr}│{RESET}    {rgb(*THEME.ok)}✓{RESET} {filename} ({status})")
        
        lines.append(f"  {bdr}╰{'─' * (w - 2)}╯{RESET}")
        
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()
        
    except Exception as e:
        # Silent fail - preview is non-critical
        pass


def confirm_git_commit() -> bool:
    """Interactive confirmation for git commit.
    
    Returns:
        True if user confirms
    """
    print(f"\n  {BOLD}Auto-Commit Confirmation{RESET}")
    print(f"  {DIM}This will commit documentation changes to git.{RESET}")
    print(f"\n  Commit message format:")
    print(f"    docs(breakthrough): [Pattern Name]")
    print(f"\n  {rgb(*THEME.wrn)}⚠ Use --force to skip this prompt{RESET}")
    
    try:
        response = input(f"\n  Proceed? [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        return False


# ── Matrix rain (easter egg, --matrix flag) ──
def matrix_rain(duration=3):
    cols = shutil.get_terminal_size().columns
    chars = "アイウエオカキクケコサシスセソタチツテト01"
    for _ in range(duration * 15):
        line = "".join(random.choice(chars) for _ in range(cols))
        g = random.randint(60, 220)
        sys.stdout.write(f"{rgb(0, g, 0)}{line}{RESET}\n")
        time.sleep(0.04)
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


# ── Cheat sheet ──
def show_cheat():
    print(f"""
  {BOLD}SynapseScanner CLI v1.3.0{RESET}

  {DIM}USAGE{RESET}
    synapsescanner [QUERY] [OPTIONS]

  {DIM}BASIC EXAMPLES{RESET}
    synapsescanner                        Fetch recent papers
    synapsescanner "quantum entanglement" Search for a topic
    synapsescanner "CRISPR" --max-results 5

  {DIM}MULTI-SOURCE SEARCH{RESET}
    synapsescanner "AI" --sources arxiv,semantic_scholar
    synapsescanner "CRISPR" --sources arxiv,pubmed,biorxiv

  {DIM}AI DIGEST (requires Ollama or OpenAI){RESET}
    synapsescanner "quantum" --summarize
    SYNAPSE_AI=ollama synapsescanner "neural networks"

  {DIM}RABBIT HOLES (reference tracing){RESET}
    synapsescanner "graphene" --depth 2

  {DIM}EXPORT OPTIONS{RESET}
    synapsescanner "physics" --json > papers.json
    synapsescanner "biology" --md > note.md
    synapsescanner "AI" --export-obsidian ~/MyVault

  {DIM}WATCH MODE{RESET}
    synapsescanner "quantum" --watch
    synapsescanner "AI" --watch --notify

  {DIM}OPTIONS{RESET}
    --max-results N       Papers to fetch (default 15)
    --sources LIST        Comma-separated source list
    --fresh               Bypass cache
    --summarize           Enable AI summarization
    --depth N             Rabbit hole depth (0-3)
    --watch               Loop forever (6hr intervals)
    --notify              Webhook notifications
    --json                JSON output
    --md                  Markdown output
    --noir                Greyscale mode
    --matrix              Matrix rain easter egg
    --cheat               This screen

  {DIM}ENVIRONMENT{RESET}
    SYNAPSE_MATRIX=1      same as --matrix
    SYNAPSE_NOIR=1        same as --noir
    OPENAI_API_KEY=xxx    Enable OpenAI backend

  {DIM}PRO TIP{RESET}
    Paper URLs are {ITALIC}clickable{RESET} in Windows Terminal,
    iTerm2, and GNOME Terminal.
""")
