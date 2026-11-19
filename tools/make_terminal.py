#!/usr/bin/env python3
"""Generate assets/terminal.svg: a short terminal session that types itself out.

SMIL only (no CSS keyframes, no scripts), so it animates inside GitHub's <img> sandbox.
Edit SESSION and rerun: python3 tools/make_terminal.py
"""
from html import escape
from pathlib import Path

SESSION = [
    ("whoami", [("khalil ammar", "ink"), (" · aka fadigaa", "dim")]),
    ("cat studies.txt", [("networks & telecom engineering · INSAT, Tunis", "body")]),
    ("cat role.txt", [("securinets insat · reverse engineering team", "body")]),
    ("ltrace ./doorman", [('strcmp("hello", "SHIFT-', "body"), ("████", "acc"), ('-NIGHT") = 21', "body")]),
    ("cat skills.txt", [("[+] ", "ok"), ("reversing · android & iOS · detection", "body")]),
    ("echo $LANG", [("ar · fr · en", "mem")]),
]

W, FONT, LINE, PAD_X, TOP = 640, 15, 24, 22, 58
CHAR = FONT * 0.6          # monospace advance
TYPE_MS, PAUSE_MS, START_MS = 55, 380, 600
COLORS = {"ink": "#F1EAE3", "body": "#D2C7BE", "dim": "#998E86", "acc": "#F2C9A8",
          "ok": "#9FD3A4", "mem": "#9DB6DA", "prompt": "#F2C9A8"}
BG, BAR, EDGE = "#0D0B0A", "#171312", "#2A2321"


def span(text, color):
    return f'<tspan fill="{COLORS[color]}">{escape(text)}</tspan>'


def typed_line(y, cmd, begin_ms, idx):
    """Prompt + command revealed one character at a time via a stepped clip rect."""
    x0 = PAD_X + 2 * CHAR
    steps = ";".join(f"{(i * CHAR):.1f}" for i in range(len(cmd) + 1))
    dur = TYPE_MS * len(cmd)
    clip = (f'<clipPath id="c{idx}"><rect x="{x0}" y="{y - FONT}" height="{LINE}" width="0">'
            f'<animate attributeName="width" values="{steps}" calcMode="discrete" '
            f'begin="{begin_ms}ms" dur="{dur}ms" fill="freeze"/></rect></clipPath>')
    prompt = (f'<text x="{PAD_X}" y="{y}" opacity="0">{span("$", "prompt")}'
              f'<set attributeName="opacity" to="1" begin="{begin_ms - 200}ms" fill="freeze"/></text>')
    body = f'<text x="{x0}" y="{y}" clip-path="url(#c{idx})" fill="{COLORS["ink"]}">{escape(cmd)}</text>'
    return clip + prompt + body, begin_ms + dur


def output_line(y, parts, begin_ms):
    inner = "".join(span(t, c) for t, c in parts)
    return (f'<text x="{PAD_X}" y="{y}" opacity="0">{inner}'
            f'<set attributeName="opacity" to="1" begin="{begin_ms}ms" fill="freeze"/></text>')


def build():
    out, t, y = [], START_MS, TOP
    for i, (cmd, result) in enumerate(SESSION):
        svg, t = typed_line(y, cmd, t, i)
        out.append(svg)
        t += PAUSE_MS // 2
        out.append(output_line(y + LINE, result, t))
        t += PAUSE_MS
        y += LINE * 2 + 6
    cursor_x = PAD_X + 2 * CHAR
    out.append(f'<text x="{PAD_X}" y="{y}" opacity="0">{span("$", "prompt")}'
               f'<set attributeName="opacity" to="1" begin="{t}ms" fill="freeze"/></text>')
    out.append(f'<rect x="{cursor_x}" y="{y - FONT + 2}" width="{CHAR:.1f}" height="{FONT + 2}" '
               f'fill="{COLORS["acc"]}" opacity="0"><animate attributeName="opacity" values="0;1;1;0" '
               f'keyTimes="0;0.01;0.5;0.51" dur="1.1s" begin="{t}ms" repeatCount="indefinite"/></rect>')
    h = y + 26
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="t d">
<title id="t">fadigaa@insat terminal</title>
<desc id="d">A terminal session introducing Khalil Ammar, aka fadigaa: networks and telecommunications engineering student at INSAT, Tunis; reverse engineering team at Securinets INSAT; reverse engineering, Android and iOS security, detection; speaks Arabic, French and English.</desc>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="{BAR}"/>
<circle cx="20" cy="16" r="5" fill="#3E3532"/><circle cx="37" cy="16" r="5" fill="#3E3532"/><circle cx="54" cy="16" r="5" fill="#3E3532"/>
<text x="{W / 2}" y="20" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12" fill="{COLORS["dim"]}">fadigaa@insat: ~</text>
<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" font-size="{FONT}" xml:space="preserve">
{chr(10).join(out)}
</g>
</svg>
'''


if __name__ == "__main__":
    dest = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest}")
