#!/usr/bin/env python3
"""Generate assets/terminal.svg: a terminal window whose text types itself out.

SMIL only (no CSS keyframes, no scripts), so it animates inside GitHub's <img> sandbox.
Edit LINES and rerun: python3 tools/make_terminal.py
Each line is a list of (text, colour) parts; None is a blank spacer line.
"""
from html import escape
from pathlib import Path

H1 = 22  # heading font size
LINES = [
    ("h1", [("Khalil Ammar", "ink"), ("  aka fadigaa", "dim")]),
    None,
    ("p", [("Cybersecurity", "acc"), (" enthusiast and engineering student. I like", "body")]),
    ("p", [("finding out how systems really work, and then how they", "body")]),
    ("p", [("break: ", "body"), ("reverse engineering", "acc"), (", web and mobile apps, networks", "body")]),
    ("p", [("and the detections that are supposed to catch it all.", "body")]),
    None,
    ("p", [("Networks & telecom engineering at ", "body"), ("INSAT", "ink"), (", Tunis.", "body")]),
    ("p", [("Technical team at ", "body"), ("Securinets INSAT", "ink"), (": I write CTF", "body")]),
    ("p", [("challenges, run workshops and help first-years get started.", "body")]),
    ("p", [("Off hours I play CTFs with ", "body"), ("MOJO-JOJO", "ink"), (".", "body")]),
]

W, FONT, LINE, BLANK, PAD_X, TOP = 640, 15, 24, 12, 26, 68
TYPE_MS, LINE_PAUSE_MS, START_MS = 16, 90, 500
COLORS = {"ink": "#F1EAE3", "body": "#D2C7BE", "dim": "#998E86", "acc": "#F2C9A8", "mem": "#9DB6DA"}
BG, BAR, EDGE, DOT = "#0D0B0A", "#171312", "#2A2321", "#3E3532"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def tspans(parts):
    # Every space is non-breaking: SVG collapses runs of spaces, which would break the label column.
    return "".join(f'<tspan fill="{COLORS[c]}">{escape(t).replace(" ", "\u00a0")}</tspan>' for t, c in parts)


def typed(idx, y, size, parts, begin):
    """Reveal a line one character at a time with a stepped clip rectangle."""
    char = size * 0.6
    n = sum(len(t) for t, _ in parts)
    steps = ";".join(f"{i * char:.1f}" for i in range(n + 1))
    dur = max(TYPE_MS * n, 1)
    weight = ' font-weight="700"' if size == H1 else ""
    svg = (f'<clipPath id="c{idx}"><rect x="{PAD_X}" y="{y - size - 2}" height="{size + 10}" width="0">'
           f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="{begin}ms" '
           f'dur="{dur}ms" fill="freeze"/></rect></clipPath>'
           f'<text x="{PAD_X}" y="{y}" font-size="{size}"{weight} clip-path="url(#c{idx})">{tspans(parts)}</text>')
    return svg, begin + dur, PAD_X + n * char


def build():
    out, t, y, end_x = [], START_MS, TOP, PAD_X
    for i, line in enumerate(LINES):
        if line is None:
            y += BLANK
            continue
        kind, parts = line
        size = H1 if kind == "h1" else FONT
        svg, t, end_x = typed(i, y, size, parts, t)
        out.append(svg)
        t += LINE_PAUSE_MS
        y += LINE + (8 if kind == "h1" else 0)
    last_y = y - LINE
    out.append(f'<rect x="{end_x + 4:.1f}" y="{last_y - FONT + 2}" width="{FONT * 0.6:.1f}" height="{FONT + 2}" '
               f'fill="{COLORS["acc"]}" opacity="0"><animate attributeName="opacity" values="0;1;1;0" '
               f'keyTimes="0;0.01;0.5;0.51" dur="1.1s" begin="{t}ms" repeatCount="indefinite"/></rect>')
    h = y + 10
    alt = " ".join(t for line in LINES if line for t, _ in line[1])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="t d">
<title id="t">Khalil Ammar</title>
<desc id="d">{escape(alt)}</desc>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="{BAR}"/>
<circle cx="20" cy="16" r="5" fill="{DOT}"/><circle cx="37" cy="16" r="5" fill="{DOT}"/><circle cx="54" cy="16" r="5" fill="{DOT}"/>
<text x="{W / 2}" y="20" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{COLORS["dim"]}">fadigaa@insat: ~/about</text>
<g font-family="{MONO}" xml:space="preserve">
{chr(10).join(out)}
</g>
</svg>
'''


if __name__ == "__main__":
    dest = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest}")
