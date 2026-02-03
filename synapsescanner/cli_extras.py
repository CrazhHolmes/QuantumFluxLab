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
    title    = "SynapseScanner v1.0.0"
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
  {BOLD}SynapseScanner CLI{RESET}

  {DIM}FLAGS{RESET}
    --max-results N   Papers to fetch (default 15)
    --noir            Greyscale mode
    --matrix          Matrix rain easter egg
    --cheat           This screen

  {DIM}ENVIRONMENT{RESET}
    SYNAPSE_MATRIX=1  same as --matrix
    SYNAPSE_NOIR=1    same as --noir

  {DIM}PRO TIP{RESET}
    Paper URLs in the progress line are {ITALIC}clickable{RESET}
    in Windows Terminal, iTerm2, and GNOME Terminal.
""")
