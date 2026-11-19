#!/usr/bin/env python3
"""Render the animated SVG cards for the DavidFrings GitHub profile README.

The cards are embedded through <img> tags, so every SVG is fully self-contained:
an inline <style> block with CSS keyframes, SMIL <animate> elements and fonts that
are subset with pyftsubset and embedded as base64 WOFF data URIs. No scripts, no
external requests.

Usage:
    python scripts/profile_cards.py fetch            # refresh data/github.json (needs GH_TOKEN)
    python scripts/profile_cards.py render           # write cards/*.svg + README card block
    STATIC=1 python scripts/profile_cards.py render  # final frame only -> preview/ (for screenshots)

Environment:
    GH_TOKEN       token for `fetch` (read:user scope to include private contributions)
    PROFILE_EMAIL  address shown on the email tile
    STATIC=1       render the final frame without any animation
    OUT_DIR        override the output directory

Requirements: Python 3.11+, fonttools (pip install fonttools).
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import urllib.request
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "github.json"
FONT_DIR = ROOT / "assets" / "fonts"
README = ROOT / "README.md"
README_START = "<!--START_SECTION:cards-->"
README_END = "<!--END_SECTION:cards-->"

PROFILE = {
    "login": "DavidFrings",
    "first_name": "David",
    "last_name": "Frings",
    "tagline": "CS student at Hochschule München · Rust, embedded systems & homelab",
    "status": "Hello, world",
    # Optional portrait, path relative to the repo root (jpg/png/webp), e.g. "assets/portrait.jpg".
    "portrait": None,
}

# The contact address comes from the environment (a repository variable in the workflow)
# instead of being hard-coded here.
EMAIL_ENV = "PROFILE_EMAIL"
EMAIL_PLACEHOLDER = "you@example.dev"


def tiles() -> list[dict]:
    email = os.environ.get(EMAIL_ENV, "").strip()
    if not email:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            sys.exit(f"{EMAIL_ENV} is not set - add it as a repository variable (Settings > Variables > Actions)")
        print(f"warning: {EMAIL_ENV} not set, using placeholder {EMAIL_PLACEHOLDER}", file=sys.stderr)
        email = EMAIL_PLACEHOLDER
    return [
        {"slug": "website", "label": "Website", "value": "davidfrings.dev",
         "href": "https://davidfrings.dev", "icon": "globe"},
        {"slug": "linkedin", "label": "LinkedIn", "value": "in/davidfrings-dev",
         "href": "https://www.linkedin.com/in/davidfrings-dev/", "icon": "profile"},
        {"slug": "email", "label": "Email", "value": email, "href": f"mailto:{email}", "icon": "mail"},
    ]


FEATURED_REPOS = ["DavidFrings/PaRaMeRoS", "DavidFrings/MIDI-Router"]

# Used only when the repository has no description on GitHub.
REPO_FALLBACK_DESCRIPTIONS = {
    "DavidFrings/PaRaMeRoS": "Vue 3 + Vite PWA frontend with a Rust / Actix-Web and PostgreSQL (Diesel) backend.",
}

# Brand colours, taken from davidfrings.dev
GREEN = "#00C86F"
BG = "#060E09"
BG2 = "#0D1A12"
WHITE = "#E8F5EE"

FONTS = {400: "JetBrainsMono-Regular.ttf", 700: "JetBrainsMono-Bold.ttf", 800: "JetBrainsMono-ExtraBold.ttf"}
ADVANCE = 0.6  # JetBrains Mono advance width in em (600 / 1000 units)

EASE = "cubic-bezier(.2,.8,.2,1)"
CARD_WIDTH = 840  # roughly the width of a GitHub profile README column

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# --------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------

def mono_width(s: str, size: float, spacing: float = 0.0) -> float:
    """Visual width of a monospaced string (trailing letter-spacing excluded)."""
    if not s:
        return 0.0
    return len(s) * (ADVANCE * size + spacing) - spacing


def blend(fg: str, bg: str, alpha: float) -> str:
    """Alpha-blend two hex colours into a solid hex colour."""
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(fc * alpha + bc * (1 - alpha)):02X}" for fc, bc in zip(f, b))


def fmt(n: float) -> str:
    """Compact number formatting for SVG coordinates."""
    return f"{n:.2f}".rstrip("0").rstrip(".") if isinstance(n, float) else str(n)


def plural(n: int, word: str) -> str:
    return f"{n:,} {word}" if n == 1 else f"{n:,} {word}s"


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s[:10])


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def ago(then: dt.datetime, now: dt.datetime) -> str:
    days = (now.date() - then.date()).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    if days < 365:
        months = days // 30
        return "1 month ago" if months == 1 else f"{months} months ago"
    years = days // 365
    return "1 year ago" if years == 1 else f"{years} years ago"


# --------------------------------------------------------------------------------------
# Font subsetting
# --------------------------------------------------------------------------------------

_cmaps: dict[int, set[int]] = {}


def check_glyphs(weight: int, chars: set[str]) -> None:
    """Warn about characters the font cannot render."""
    if weight not in _cmaps:
        from fontTools.ttLib import TTFont
        _cmaps[weight] = set(TTFont(FONT_DIR / FONTS[weight]).getBestCmap())
    missing = sorted(c for c in chars if ord(c) not in _cmaps[weight] and not c.isspace())
    if missing:
        print(f"warning: font weight {weight} has no glyph for {''.join(missing)!r}", file=sys.stderr)


def subset_font(weight: int, chars: set[str]) -> str:
    """Subset the font to the given characters with pyftsubset and return base64 WOFF."""
    check_glyphs(weight, chars)
    with tempfile.TemporaryDirectory() as tmp:
        text_file = Path(tmp) / "chars.txt"
        out_file = Path(tmp) / "font.woff"
        text_file.write_text("".join(sorted(chars)), encoding="utf-8")
        # `python -m fontTools.subset` is the pyftsubset entry point; using it this way
        # avoids depending on the console script being on PATH.
        subprocess.run(
            [sys.executable, "-m", "fontTools.subset", str(FONT_DIR / FONTS[weight]),
             f"--text-file={text_file}", "--flavor=woff", f"--output-file={out_file}",
             "--no-hinting", "--desubroutinize", "--name-IDs=1,2"],
            check=True,
        )
        return base64.b64encode(out_file.read_bytes()).decode("ascii")


# --------------------------------------------------------------------------------------
# Card builder
# --------------------------------------------------------------------------------------

ANIMATION_CSS = """
.s{display:none}
.dr{stroke-dasharray:1}
.fb{transform-box:fill-box;transform-origin:0 50%}
.fc{transform-box:fill-box;transform-origin:50% 50%}
@keyframes fu{from{opacity:0;transform:translateY(10px)}}
@keyframes fi{from{opacity:0}}
@keyframes dr{from{stroke-dashoffset:1}}
@keyframes ol{from{stroke-dasharray:0 320}to{stroke-dasharray:320 0}}
@keyframes bl{50%{opacity:.2}}
@keyframes cb{50%{opacity:0}}
@keyframes gx{from{transform:scaleX(0)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.m{display:none}.s{display:inline}}
"""

BASE_CSS = f"""
text{{font-family:'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.w{{fill:{WHITE}}}
.g{{fill:{GREEN}}}
.mu{{fill:{WHITE};fill-opacity:.45}}
.dim{{fill:{WHITE};fill-opacity:.7}}
.ln{{fill:none;stroke:{GREEN};stroke-opacity:.2}}
.br{{fill:none;stroke:{GREEN};stroke-width:2}}
"""


class Card:
    """Collects SVG markup, CSS and the glyphs each font weight needs."""

    def __init__(self, slug: str, width: int, height: int, start: float, static: bool):
        self.slug = slug
        self.width = width
        self.height = height
        self.start = start  # card offset on the page-wide timeline (seconds)
        self.static = static
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.css: list[str] = []
        self.chars: dict[int, set[str]] = defaultdict(set)

    # -- timing -------------------------------------------------------------------------

    def t(self, local: float) -> float:
        """Absolute time (seconds since load) for a card-local delay."""
        return round(self.start + local, 3)

    def anim(self, name: str, local: float, dur: float, ease: str = EASE, extra: str = "") -> str:
        """CSS animation declaration; empty in static mode. Base styles are the final frame."""
        if self.static:
            return ""
        decl = f"{name} {dur}s {ease} {self.t(local)}s both"
        return f"animation:{decl}{', ' + extra if extra else ''};"

    def swap(self, animated: str, still: str) -> str:
        """SMIL content plus a static twin that is shown under prefers-reduced-motion.

        CSS cannot pause SMIL, so the animated version is hidden and the still one shown.
        """
        if self.static:
            return still
        return f'<g class="m">{animated}</g><g class="s">{still}</g>'

    # -- primitives ---------------------------------------------------------------------

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, s: str, *, size: float, weight: int = 400, cls: str = "w",
             spacing: float | None = None, anchor: str | None = None, style: str = "",
             attrs: str = "") -> str:
        self.chars[weight].update(s)
        css = f"font-size:{fmt(size)}px;"
        if weight != 400:
            css += f"font-weight:{weight};"
        if spacing:
            css += f"letter-spacing:{fmt(spacing)}px;"
        css += style
        anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
        cls_attr = f' class="{cls}"' if cls else ""
        return (f'<text x="{fmt(x)}" y="{fmt(y)}"{cls_attr}{anchor_attr} style="{css}"{attrs}>'
                f"{escape(s)}</text>")

    def label(self, x: float, y: float, s: str, *, cls: str = "mu", anchor: str | None = None,
              style: str = "") -> str:
        """Uppercase, letter-spaced label like the status pill on davidfrings.dev."""
        return self.text(x, y, s.upper(), size=10, spacing=2, cls=cls, anchor=anchor, style=style)

    def frame(self, grid: bool = False) -> None:
        """Card surface, 1px border, optional grid and the green corner brackets."""
        w, h = self.width, self.height
        self.add(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="{BG2}" stroke="{GREEN}" '
                 f'stroke-opacity=".2" style="{self.anim("fi", 0, .5)}"/>')
        if grid:
            self.defs.append(
                f'<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">'
                f'<path d="M48 0H0V48" fill="none" stroke="{GREEN}" stroke-opacity=".2"/></pattern>'
                f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
                f'<stop offset="1" stop-color="#fff" stop-opacity=".15"/></linearGradient>'
                f'<mask id="gridmask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>')
            self.add(f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="url(#grid)" opacity=".35" '
                     f'mask="url(#gridmask)" style="{self.anim("fi", .1, 1.2, "ease-out")}"/>')
        draw = self.anim("dr", .05, .7)
        self.add(f'<path class="br dr" pathLength="1" d="M1 17V1H17" style="{draw}"/>')
        self.add(f'<path class="br dr" pathLength="1" d="M{w - 1} {h - 17}V{h - 1}H{w - 17}" style="{draw}"/>')

    # -- output -------------------------------------------------------------------------

    def render(self, title: str, desc: str) -> str:
        font_css = "".join(
            f"@font-face{{font-family:'JBM';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff;base64,{subset_font(weight, chars)}) format('woff')}}"
            for weight, chars in sorted(self.chars.items()) if chars
        )
        css = font_css + BASE_CSS + ("" if self.static else ANIMATION_CSS) + "".join(self.css)
        css = re.sub(r"\n\s*", "", css)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
            f"<style>{css}</style>{defs}\n" + "\n".join(self.parts) + "\n</svg>\n"
        )


# --------------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------------

def load_data() -> dict:
    if not DATA_FILE.exists():
        sys.exit(f"{DATA_FILE.relative_to(ROOT)} not found - run `python scripts/profile_cards.py fetch` first")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def contribution_stats(days: list[dict]) -> dict:
    counts = [d["count"] for d in days]
    dates = [parse_date(d["date"]) for d in days]

    # Today is usually still in progress, so a streak only breaks on an empty *past* day.
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1

    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    busiest_idx = max(range(len(counts)), key=lambda k: (counts[k], k)) if counts else 0

    # Last twelve calendar months, including the current (partial) one.
    last = dates[-1]
    months = []
    y, m = last.year, last.month
    for _ in range(12):
        months.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    months.reverse()
    per_month = {ym: 0 for ym in months}
    for d, c in zip(dates, counts):
        if (d.year, d.month) in per_month:
            per_month[(d.year, d.month)] += c

    return {
        "total": sum(counts),
        "current_streak": current,
        "longest_streak": longest,
        "active_days": sum(1 for c in counts if c > 0),
        "days": len(counts),
        "busiest_date": dates[busiest_idx],
        "busiest_count": counts[busiest_idx],
        "months": [(ym, per_month[ym]) for ym in months],
        "last_date": last,
    }


# --------------------------------------------------------------------------------------
# Icons (24x24, stroked) - drawn by hand to stay on brand
# --------------------------------------------------------------------------------------

ICONS = {
    "globe": ["M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0",
              "M12 3a4.5 9 0 1 0 0 18a4.5 9 0 1 0 0 -18",
              "M3.5 12H20.5", "M5 7.5H19", "M5 16.5H19"],
    "profile": ["M3 4H21V20H3Z",
                "M9.2 9.6a2.8 2.8 0 1 0 5.6 0a2.8 2.8 0 1 0 -5.6 0",
                "M6.5 17.5c.9-2.6 2.9-4 5.5-4s4.6 1.4 5.5 4"],
    "mail": ["M3 6H21V18H3Z", "M3 6.5L12 13L21 6.5"],
    "arrow": ["M5 19L19 5", "M8 5H19V16"],
}

STAR = "M6 .9 7.6 4.2l3.7.5-2.7 2.5.7 3.6L6 9 2.7 10.8l.7-3.6L.7 4.7l3.7-.5Z"
FORK = ("M1.6 2.2a1.4 1.4 0 1 0 2.8 0a1.4 1.4 0 1 0 -2.8 0M7.6 2.2a1.4 1.4 0 1 0 2.8 0a1.4 1.4 0 1 0 -2.8 0"
        "M4.6 9.8a1.4 1.4 0 1 0 2.8 0a1.4 1.4 0 1 0 -2.8 0M3 3.6v.9c0 1.4 1 2.1 3 2.1s3-.7 3-2.1v-.9M6 6.6v1.8")


def icon(card: Card, name: str, x: float, y: float, local: float, scale: float = 1.0) -> str:
    style = card.anim("dr", local, .9, "ease-in-out")
    paths = "".join(f'<path class="dr" pathLength="1" d="{d}" style="{style}"/>' for d in ICONS[name])
    return (f'<g transform="translate({fmt(x)} {fmt(y)}) scale({fmt(scale)})" fill="none" stroke="{GREEN}" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths}</g>')


# --------------------------------------------------------------------------------------
# Cards
# --------------------------------------------------------------------------------------

def card_hero(start: float, static: bool) -> Card:
    w, h = CARD_WIDTH, 230
    c = Card("hero", w, h, start, static)
    c.frame(grid=True)

    portrait = PROFILE.get("portrait")
    portrait_path = ROOT / portrait if portrait else None
    if portrait_path and not portrait_path.exists():
        print(f"warning: portrait {portrait} not found, rendering without it", file=sys.stderr)
        portrait_path = None

    centered = portrait_path is None
    left = 56

    def x_for(width: float) -> float:
        return (w - width) / 2 if centered else left

    # Status pill with the blinking dot
    status = PROFILE["status"].upper()
    status_w = mono_width(status, 10, 2)
    pill_w = 14 + 7 + 9 + status_w + 14
    px, py = x_for(pill_w), 32
    blink = "" if static else f"bl 2.5s ease-in-out {c.t(1)}s infinite"
    c.add(f'<g style="{c.anim("fu", .1, .6)}">'
          f'<rect x="{fmt(px)}" y="{py}" width="{fmt(pill_w)}" height="26" class="ln"/>'
          f'<circle cx="{fmt(px + 17.5)}" cy="{py + 13}" r="3.5" class="g" style="{c.anim("fi", .2, .3, extra=blink)}"/>'
          + c.label(px + 30, py + 17, status, cls="g") + "</g>")

    # Name: "David" solid, "Frings" outlined in green and drawn stroke by stroke
    size, spacing = 54, -1
    first, last = PROFILE["first_name"], PROFILE["last_name"]
    full_w = mono_width(f"{first} {last}", size, spacing)
    nx, ny = x_for(full_w), 124
    lx = nx + (len(first) + 1) * (ADVANCE * size + spacing)
    c.add(c.text(nx, ny, first, size=size, weight=800, spacing=spacing, style=c.anim("fu", .25, .7)))
    outline = c.anim("ol", .45, 1.6, "ease-in-out") + ("" if static else "stroke-dasharray:320 0;")
    c.add(c.text(lx, ny, last, size=size, weight=800, spacing=spacing, cls="",
                 attrs=f' fill="none" stroke="{GREEN}" stroke-width="1.5"', style=outline))

    # Tagline, typed out with SMIL (discrete steps keep the monospace rhythm)
    tag = PROFILE["tagline"]
    tsize = 14
    adv = ADVANCE * tsize
    tag_w = mono_width(tag, tsize)
    tx, ty = x_for(tag_w), 172
    if not centered:
        max_chars = int((w - left - 230) / adv)
        if len(tag) > max_chars:
            print("warning: tagline is too long for the portrait layout", file=sys.stderr)
    still = (c.text(tx, ty, tag, size=tsize, cls="dim")
             + f'<rect x="{fmt(tx + tag_w + 4)}" y="{ty - 13}" width="8" height="16" class="g"/>')
    if static:
        c.add(still)
    else:
        begin, step = c.t(.9), .028
        n = len(tag)
        total = begin + n * step
        key_times = ["0"] + [f"{(begin + i * step) / total:.4f}" for i in range(1, n + 1)]
        key_times[-1] = "1"
        widths = ["0"] + [fmt(2 + i * adv) for i in range(1, n + 1)]
        xs = [fmt(tx + 4)] + [fmt(tx + i * adv + 4) for i in range(1, n + 1)]
        c.defs.append(
            f'<clipPath id="type"><rect x="{fmt(tx - 2)}" y="{ty - 16}" width="{fmt(tag_w + 4)}" height="24">'
            f'<animate attributeName="width" calcMode="discrete" dur="{total:.3f}s" fill="freeze" '
            f'values="{";".join(widths)}" keyTimes="{";".join(key_times)}"/></rect></clipPath>')
        cursor_style = (f"animation:fi .3s ease {max(begin - .3, 0):.2f}s both, "
                        f"cb 1.1s step-end {total:.2f}s infinite;")
        animated = (
            c.text(tx, ty, tag, size=tsize, cls="dim", attrs=' clip-path="url(#type)"')
            + f'<rect x="{fmt(tx + tag_w + 4)}" y="{ty - 13}" width="8" height="16" class="g" style="{cursor_style}">'
            f'<animate attributeName="x" calcMode="discrete" dur="{total:.3f}s" fill="freeze" '
            f'values="{";".join(xs)}" keyTimes="{";".join(key_times)}"/></rect>'
        )
        c.add(c.swap(animated, still))

    # Optional portrait on the right
    if portrait_path:
        mime = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}.get(portrait_path.suffix.lower(), "png")
        data = base64.b64encode(portrait_path.read_bytes()).decode("ascii")
        s = 150
        ix, iy = w - 56 - s, (h - s) / 2
        c.defs.append(f'<clipPath id="pc"><rect x="{ix}" y="{fmt(iy)}" width="{s}" height="{s}"/></clipPath>')
        draw = c.anim("dr", .6, .8)
        c.add(f'<g style="{c.anim("fi", .4, .9, "ease-out")}">'
              f'<image href="data:image/{mime};base64,{data}" x="{ix}" y="{fmt(iy)}" width="{s}" height="{s}" '
              f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>'
              f'<rect x="{ix + .5}" y="{fmt(iy + .5)}" width="{s - 1}" height="{s - 1}" class="ln"/></g>'
              f'<path class="br dr" pathLength="1" d="M{ix - 4} {fmt(iy + 12)}V{fmt(iy - 4)}H{ix + 12}" style="{draw}"/>'
              f'<path class="br dr" pathLength="1" d="M{ix + s + 4} {fmt(iy + s - 12)}V{fmt(iy + s + 4)}H{ix + s - 12}" style="{draw}"/>')
    return c


def card_tile(tile: dict, start: float, static: bool) -> Card:
    w, h = 272, 112
    c = Card(f"tile-{tile['slug']}", w, h, start, static)
    c.frame()
    c.add(icon(c, tile["icon"], 22, 22, .15))
    c.add(icon(c, "arrow", w - 38, 22, .45, scale=.7))
    c.add(c.label(22, 76, tile["label"], style=c.anim("fu", .25, .6)))
    value_size = 13 if mono_width(tile["value"], 13) <= w - 44 else 11
    c.add(c.text(22, 96, tile["value"], size=value_size, weight=700, cls="g", style=c.anim("fu", .35, .6)))
    return c


def card_activity(stats: dict, generated: dt.datetime, start: float, static: bool) -> Card:
    w = CARD_WIDTH
    top, base = 196, 306
    h = base + 52
    c = Card("activity", w, h, start, static)
    c.frame()

    c.add(c.label(32, 44, "Contributions", cls="g", style=c.anim("fu", .1, .6))
          + c.label(32 + mono_width("CONTRIBUTIONS ", 10, 2) + 2, 44, "/ last 12 months", style=c.anim("fu", .1, .6)))
    as_of = f"as of {generated.day} {MONTHS[generated.month - 1]} {generated.year}"
    c.add(c.label(w - 32, 44, as_of, anchor="end", style=c.anim("fi", .2, .6)))

    busiest = stats["busiest_date"]
    blocks = [
        ("Total", f"{stats['total']:,}", "contributions"),
        ("Current streak", plural(stats["current_streak"], "day"), f"longest {plural(stats['longest_streak'], 'day')}"),
        ("Active days", f"{stats['active_days']:,}",
         f"of {stats['days']} · {round(100 * stats['active_days'] / max(stats['days'], 1))}%"),
        ("Busiest day", f"{MONTHS[busiest.month - 1]} {busiest.day}",
         f"{plural(stats['busiest_count'], 'contribution')} · {WEEKDAYS[busiest.weekday()]}"),
    ]
    col_w = (w - 64) / 4
    for i, (label, value, sub) in enumerate(blocks):
        x = 32 + i * col_w
        d = .2 + i * .1
        if i:
            c.add(f'<path class="ln dr" pathLength="1" d="M{fmt(x - 16)} 70V140" style="{c.anim("dr", d, .5)}"/>')
        c.add(c.label(x, 82, label, style=c.anim("fu", d, .6))
              + c.text(x, 118, value, size=28, weight=800, cls="g" if i == 0 else "w", spacing=-.5,
                       style=c.anim("fu", d + .05, .6))
              + c.text(x, 140, sub, size=11, cls="mu", style=c.anim("fu", d + .1, .6)))

    c.add(f'<path class="ln dr" pathLength="1" d="M32 164H{w - 32}" style="{c.anim("dr", .5, .8, "ease-in-out")}"/>')

    # Monthly bars
    months = stats["months"]
    peak = max((v for _, v in months), default=0) or 1
    chart_h = base - top
    slot = (w - 64) / len(months)
    bar_w = min(36.0, slot * .56)
    c.defs.append(f'<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN}" stop-opacity=".25"/>'
                  f'</linearGradient>')
    c.add(f'<path d="M32 {top}H{w - 32}" class="ln" stroke-dasharray="2 4" style="{c.anim("fi", .6, .6)}"/>')
    c.add(f'<path d="M32 {base}.5H{w - 32}" class="ln" style="{c.anim("fi", .6, .6)}"/>')

    animated_bars, still_bars = [], []
    for i, ((y, m), value) in enumerate(months):
        x = 32 + i * slot + (slot - bar_w) / 2
        bh = 0 if value == 0 else max(2.0, chart_h * value / peak)
        by = base - bh
        fill = GREEN if value == peak else "url(#bar)"
        delay = c.t(.7 + i * .06)
        dur = .8
        total = delay + dur
        k = f"{delay / total:.4f}"
        rect = f'<rect x="{fmt(x)}" y="{fmt(by)}" width="{fmt(bar_w)}" height="{fmt(bh)}" fill="{fill}"'
        if bh:
            still_bars.append(rect + "/>")
            animated_bars.append(
                rect + ">"
                f'<animate attributeName="height" values="0;0;{fmt(bh)}" keyTimes="0;{k};1" dur="{total:.3f}s" '
                f'calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/>'
                f'<animate attributeName="y" values="{base};{base};{fmt(by)}" keyTimes="0;{k};1" dur="{total:.3f}s" '
                f'calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/></rect>')
        cx = x + bar_w / 2
        local = .7 + i * .06
        if value:
            c.add(c.text(cx, by - 7, f"{value:,}", size=10, weight=700 if value == peak else 400,
                         cls="g" if value == peak else "mu", anchor="middle", style=c.anim("fi", local + .6, .4)))
        c.add(c.text(cx, base + 20, MONTHS[m - 1], size=10, cls="dim" if value else "mu", anchor="middle",
                     style=c.anim("fi", local, .4)))
        if m == 1 or i == 0:
            c.add(c.text(cx, base + 34, str(y), size=9, cls="mu", anchor="middle", style=c.anim("fi", local, .4)))
    c.add(c.swap("".join(animated_bars), "".join(still_bars)))
    return c


def card_repo(repo: dict, index: int, generated: dt.datetime, start: float, static: bool) -> Card:
    w = CARD_WIDTH
    owner, name = repo["name_with_owner"].split("/", 1)
    description = (repo.get("description") or REPO_FALLBACK_DESCRIPTIONS.get(repo["name_with_owner"])
                   or "No description yet.")
    desc_size = 13
    lines = textwrap.wrap(description, width=int((w - 64) / (ADVANCE * desc_size)))
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1][:-1].rstrip() + "…"
    topics = repo.get("topics") or []

    y_desc = 116
    y = y_desc + (len(lines) - 1) * 20
    y_topics = y + 18 if topics else None
    y_bar = (y_topics + 20 if topics else y) + 24
    y_legend = y_bar + 30
    h = y_legend + 26
    c = Card(f"repo-{name.lower()}", w, h, start, static)
    c.frame()

    c.add(c.label(32, 44, f"Featured repo / {index + 1:02d}", style=c.anim("fu", .1, .6)))

    # Stars and forks, right-aligned
    x = w - 32
    meta = []
    for count, path in ((repo.get("forks", 0), FORK), (repo.get("stars", 0), STAR)):
        label = f"{count:,}"
        x -= mono_width(label, 12)
        meta.append(c.text(x, 44, label, size=12, weight=700, cls="w"))
        x -= 18
        meta.append(f'<path d="{path}" transform="translate({fmt(x)} 33.5)" fill="none" stroke="{GREEN}" '
                    f'stroke-width="1.2" stroke-linejoin="round"/>')
        x -= 18
    c.add(f'<g style="{c.anim("fi", .25, .6)}">{"".join(meta)}</g>')

    size = 26
    c.add(c.text(32, 84, f"{owner}/", size=size, cls="mu", spacing=-.5, style=c.anim("fu", .15, .6))
          + c.text(32 + mono_width(f"{owner}/", size, -.5) + 2, 84, name, size=size, weight=800, spacing=-.5,
                   style=c.anim("fu", .2, .6)))

    for i, line in enumerate(lines):
        c.add(c.text(32, y_desc + i * 20, line, size=desc_size, cls="dim", style=c.anim("fu", .3 + i * .06, .6)))

    if topics:
        tx = 32
        for i, topic in enumerate(topics[:6]):
            tw = mono_width(topic, 10) + 16
            if tx + tw > w - 32:
                break
            c.add(f'<g style="{c.anim("fu", .45 + i * .05, .5)}">'
                  f'<rect x="{fmt(tx)}" y="{y_topics}" width="{fmt(tw)}" height="20" class="ln"/>'
                  + c.text(tx + 8, y_topics + 14, topic, size=10, cls="g") + "</g>")
            tx += tw + 8

    # Language mix in shades of the brand green
    langs = repo.get("languages") or []
    total = sum(l["size"] for l in langs) or 1
    shown = [(l["name"], l["size"] / total) for l in langs[:4] if l["size"] / total >= .005]
    rest = 1 - sum(p for _, p in shown)
    if rest >= .005:
        shown.append(("Other", rest))
    shades = [1, .7, .48, .32, .2]
    bar_x, bar_w = 32, w - 64
    seg_x = bar_x
    segments = []
    for i, (lang, share) in enumerate(shown):
        seg_w = bar_w * share
        gap = 2 if i < len(shown) - 1 else 0
        segments.append(f'<rect x="{fmt(seg_x)}" y="{y_bar}" width="{fmt(max(seg_w - gap, 1))}" height="6" '
                        f'fill="{GREEN}" fill-opacity="{shades[i]}"/>')
        seg_x += seg_w
    c.add(f'<rect x="{bar_x}" y="{y_bar}" width="{bar_w}" height="6" fill="{WHITE}" fill-opacity=".05" '
          f'style="{c.anim("fi", .4, .5)}"/>'
          f'<g class="fb" style="{c.anim("gx", .55, 1.1, "cubic-bezier(.6,0,.2,1)")}">{"".join(segments)}</g>')

    lx = 32
    for i, (lang, share) in enumerate(shown):
        pct = f"{share * 100:.1f}%"
        c.add(f'<g style="{c.anim("fi", .9 + i * .08, .5)}">'
              f'<rect x="{fmt(lx)}" y="{y_legend - 8}" width="8" height="8" fill="{GREEN}" fill-opacity="{shades[i]}"/>'
              + c.text(lx + 14, y_legend, lang, size=11, cls="dim")
              + c.text(lx + 14 + mono_width(lang + " ", 11), y_legend, pct, size=11, cls="mu") + "</g>")
        lx += 14 + mono_width(f"{lang} {pct}", 11) + 22

    if repo.get("pushed_at"):
        c.add(c.text(w - 32, y_legend, f"updated {ago(parse_ts(repo['pushed_at']), generated)}", size=11,
                     cls="mu", anchor="end", style=c.anim("fi", 1.1, .5)))
    return c


def card_graph(days: list[dict], stats: dict, start: float, static: bool) -> Card:
    w = CARD_WIDTH
    top = 82
    first = parse_date(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cols = (offset + len(days) - 1) // 7 + 1
    grid_x = 66
    pitch = min(14.0, (w - 32 - grid_x) / cols)
    cell = pitch - 3
    h = int(top + 7 * pitch + 58)
    c = Card("graph", w, h, start, static)
    c.frame()

    c.add(c.label(32, 44, "Contribution graph", cls="g", style=c.anim("fu", .1, .6)))
    c.add(c.label(w - 32, 44, f"{stats['total']:,} in the last year", anchor="end", style=c.anim("fi", .2, .6)))

    colours = [blend(WHITE, BG2, .06)] + [blend(GREEN, BG2, a) for a in (.28, .5, .75, 1)]

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        c.add(c.text(32, top + row * pitch + cell - 1.5, name, size=9, cls="mu", style=c.anim("fi", .2, .5)))

    reveal_start, reveal = .35, 1.4
    if not static:
        rules = [f".cl{{animation:pop .5s {EASE} both}}"]
        rules += [f".k{i}{{animation-delay:{c.t(reveal_start + reveal * i / max(cols - 1, 1)):.3f}s}}"
                  for i in range(cols)]
        c.css.append("".join(rules))

    cells, last_label_col = [], -10
    for i, day in enumerate(days):
        idx = offset + i
        col, row = idx // 7, idx % 7
        x, y = grid_x + col * pitch, top + row * pitch
        cls = "" if static else f' class="cl fc k{col}"'
        cells.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(cell)}" height="{fmt(cell)}" rx="2" '
                     f'fill="{colours[max(0, min(4, day["level"]))]}"{cls}/>')
        d = parse_date(day["date"])
        if d.day == 1 and col - last_label_col >= 3 and col < cols - 1:
            c.add(c.text(x, top - 10, MONTHS[d.month - 1], size=9, cls="mu",
                         style=c.anim("fi", reveal_start + reveal * col / max(cols - 1, 1), .4)))
            last_label_col = col
    c.add("".join(cells))

    # A scan line sweeps across while the columns pop in (SMIL)
    if not static:
        x0, x1 = grid_x - 3, grid_x + cols * pitch
        a = c.t(reveal_start)
        end = a + reveal
        total = end + .4
        k1, k2, k3 = a / total, (a + .1) / total, end / total
        line = (f'<rect x="{x0}" y="{top - 3}" width="2" height="{fmt(7 * pitch + 3)}" fill="{GREEN}" opacity="0">'
                f'<animate attributeName="x" values="{x0};{x0};{fmt(x1)};{fmt(x1)}" keyTimes="0;{k1:.4f};{k3:.4f};1" '
                f'dur="{total:.3f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="0;0;.9;.9;0" keyTimes="0;{k1:.4f};{k2:.4f};{k3:.4f};1" '
                f'dur="{total:.3f}s" fill="freeze"/></rect>')
        c.add(c.swap(line, ""))

    # Legend
    ly = top + 7 * pitch + 30
    x = w - 32 - mono_width("More", 10)
    legend = [c.text(x, ly, "More", size=10, cls="mu")]
    x -= 8 + 5 * 14
    for i, colour in enumerate(colours):
        legend.append(f'<rect x="{fmt(x + i * 14)}" y="{fmt(ly - 9.5)}" width="11" height="11" rx="2" fill="{colour}"/>')
    x -= 8 + mono_width("Less", 10)
    legend.append(c.text(x, ly, "Less", size=10, cls="mu"))
    c.add(f'<g style="{c.anim("fi", reveal_start + reveal, .5)}">{"".join(legend)}</g>')
    c.add(c.text(32, ly, f"{stats['active_days']} active days · longest streak {plural(stats['longest_streak'], 'day')}",
                 size=10, cls="mu", style=c.anim("fi", reveal_start + reveal, .5)))
    return c


# --------------------------------------------------------------------------------------
# README block and preview page
# --------------------------------------------------------------------------------------

def readme_block(prefix: str, entries: list[dict]) -> str:
    """HTML for the card stack. Tiles share one row at 32.5% width each."""
    rows, tiles_row = [], []
    for e in entries:
        img = f'<img src="{prefix}{e["file"]}" width="{e["width"]}" alt="{escape(e["alt"], {chr(34): "&quot;"})}">'
        if e.get("href"):
            img = f'<a href="{e["href"]}">{img}</a>'
        if e["kind"] == "tile":
            tiles_row.append(img)
            continue
        if tiles_row:
            rows.append("\n".join(tiles_row))
            tiles_row = []
        rows.append(img)
    if tiles_row:
        rows.append("\n".join(tiles_row))
    return "\n".join(f'<p align="center">\n{row}\n</p>' for row in rows)


def write_preview(path: Path, block: str, static: bool) -> None:
    mode = "static final frame" if static else "animated"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Profile cards preview ({mode})</title>
<style>
  body {{ margin: 0; background: #0d1117; color: #e6edf3; font: 14px/1.5 -apple-system, "Segoe UI", sans-serif; }}
  .readme {{ box-sizing: border-box; width: 878px; margin: 24px auto; padding: 24px; border: 1px solid #30363d; border-radius: 6px; }}
  .readme p {{ margin: 0 0 16px; }}
  .readme img {{ max-width: 100%; box-sizing: content-box; }}
  .note {{ text-align: center; color: #7d8590; font-size: 12px; }}
</style></head>
<body><p class="note">Preview at GitHub's README width - {mode}</p>
<div class="readme">
{block}
</div></body></html>
""", encoding="utf-8")


# --------------------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------------------

def render() -> None:
    static = os.environ.get("STATIC") == "1"
    out_dir = Path(os.environ.get("OUT_DIR") or (ROOT / "preview" if static else ROOT / "cards"))
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_data()
    generated = parse_ts(data["generated_at"])
    stats = contribution_stats(data["days"])
    repos = {r["name_with_owner"].lower(): r for r in data.get("repos", [])}

    # Page-wide timeline: each card starts a little after the one above it.
    t = 0.0
    entries: list[tuple[Card, dict]] = []

    hero = card_hero(t, static)
    entries.append((hero, {"kind": "full", "width": "100%",
                           "alt": f"{PROFILE['first_name']} {PROFILE['last_name']} - {PROFILE['tagline']}"}))
    t += .9
    for tile in tiles():
        entries.append((card_tile(tile, t, static),
                        {"kind": "tile", "width": "32.5%", "href": tile["href"],
                         "alt": f"{tile['label']}: {tile['value']}"}))
        t += .15
    t += .3
    busiest = stats["busiest_date"]
    entries.append((card_activity(stats, generated, t, static), {
        "kind": "full", "width": "100%",
        "alt": (f"{stats['total']} contributions in the last 12 months. Current streak "
                f"{plural(stats['current_streak'], 'day')}, {stats['active_days']} active days, busiest day "
                f"{busiest.isoformat()} with {plural(stats['busiest_count'], 'contribution')}.")}))
    t += .9
    for i, full_name in enumerate(FEATURED_REPOS):
        repo = repos.get(full_name.lower())
        if not repo:
            print(f"warning: {full_name} missing from {DATA_FILE.name}; run fetch", file=sys.stderr)
            continue
        card = card_repo(repo, i, generated, t, static)
        desc = repo.get("description") or REPO_FALLBACK_DESCRIPTIONS.get(full_name, "")
        entries.append((card, {"kind": "full", "width": "100%", "href": repo["url"],
                               "alt": f"{full_name}: {desc}".strip(": ")}))
        t += .3
    entries.append((card_graph(data["days"], stats, t, static),
                    {"kind": "full", "width": "100%",
                     "alt": f"Contribution graph: {stats['total']} contributions in the last year"}))

    written = set()
    for card, meta in entries:
        file = f"{card.slug}.svg"
        svg = card.render(meta["alt"], meta["alt"])
        (out_dir / file).write_text(svg, encoding="utf-8")
        meta["file"] = file
        written.add(file)
        print(f"{out_dir.name}/{file:<24} {len(svg.encode()) / 1024:6.1f} KiB")

    # Drop cards that no longer exist (e.g. a repo removed from FEATURED_REPOS)
    for stale in out_dir.glob("*.svg"):
        if stale.name not in written:
            stale.unlink()
            print(f"removed stale {stale.name}")

    metas = [m for _, m in entries]
    if static:
        write_preview(out_dir / "index.html", readme_block("", metas), static=True)
        print(f"preview: {out_dir / 'index.html'}")
        return

    rel = os.path.relpath(out_dir, ROOT).replace(os.sep, "/") + "/"
    write_preview(ROOT / "preview" / "animated.html", readme_block(f"../{rel}", metas), static=False)
    update_readme(readme_block(rel, metas))


def update_readme(block: str) -> None:
    text = README.read_text(encoding="utf-8")
    if README_START not in text or README_END not in text:
        sys.exit(f"README.md needs {README_START} and {README_END} markers")
    head, rest = text.split(README_START, 1)
    _, tail = rest.split(README_END, 1)
    new = f"{head}{README_START}\n{block}\n{README_END}{tail}"
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md card block updated")


GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
  %s
}
fragment Repo on Repository {
  nameWithOwner url description stargazerCount forkCount pushedAt
  repositoryTopics(first: 8) { nodes { topic { name } } }
  languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
}
"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch() -> None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("set GH_TOKEN (a token with read:user scope to include private contributions)")

    aliases = "\n  ".join(
        f"r{i}: repository(owner: {json.dumps(full.split('/')[0])}, name: {json.dumps(full.split('/')[1])}) {{ ...Repo }}"
        for i, full in enumerate(FEATURED_REPOS))
    body = json.dumps({"query": GRAPHQL_QUERY % aliases, "variables": {"login": PROFILE["login"]}}).encode()
    request = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-cards"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        sys.exit(f"GraphQL errors: {json.dumps(payload['errors'], indent=2)}")
    result = payload["data"]

    calendar = result["user"]["contributionsCollection"]["contributionCalendar"]
    days = [{"date": d["date"], "count": d["contributionCount"], "level": LEVELS.get(d["contributionLevel"], 0)}
            for week in calendar["weeks"] for d in week["contributionDays"]]
    repos = []
    for i in range(len(FEATURED_REPOS)):
        r = result.get(f"r{i}")
        if not r:
            print(f"warning: {FEATURED_REPOS[i]} not found", file=sys.stderr)
            continue
        repos.append({
            "name_with_owner": r["nameWithOwner"], "url": r["url"], "description": r["description"],
            "stars": r["stargazerCount"], "forks": r["forkCount"], "pushed_at": r["pushedAt"],
            "topics": [n["topic"]["name"] for n in r["repositoryTopics"]["nodes"]],
            "languages": [{"name": e["node"]["name"], "size": e["size"]} for e in r["languages"]["edges"]],
        })

    out = {
        "login": PROFILE["login"],
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "GitHub GraphQL API",
        "total": calendar["totalContributions"],
        "days": days,
        "repos": repos,
    }
    write_data(out)
    print(f"{DATA_FILE.relative_to(ROOT)}: {len(days)} days, {out['total']} contributions, {len(repos)} repos")


def write_data(data: dict) -> None:
    """Pretty JSON with one line per day, so daily diffs stay small and readable."""
    days = data["days"]
    placeholder = "__DAYS__"
    text = json.dumps({**data, "days": placeholder}, indent=2, ensure_ascii=False)
    day_lines = ",\n".join("    " + json.dumps(d, ensure_ascii=False) for d in days)
    text = text.replace(f'"{placeholder}"', "[\n" + day_lines + "\n  ]")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(text + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["fetch", "render"], nargs="?", default="render")
    args = parser.parse_args()
    fetch() if args.command == "fetch" else render()


if __name__ == "__main__":
    main()
