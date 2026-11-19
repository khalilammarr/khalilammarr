#!/usr/bin/env python3
"""Generate assets/toolbox.svg: brand-coloured tool tiles that drop in one by one,
then a highlight that sweeps across them on a loop.

Icons are vendored from Simple Icons (CC0) in tools/icons/ with their brand colours
in tools/icons/meta.json. Tools Simple Icons doesn't carry get a monogram tile.
SMIL only, so it animates inside GitHub's <img> sandbox. Rerun after editing ROWS.
"""
import json
import re
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICONS = HERE / "icons"
META = json.loads((ICONS / "meta.json").read_text())

# (slug or None, label, monogram when there is no icon)
ROWS = [
    ("security", [("burpsuite", "Burp", ""), ("wireshark", "Wireshark", ""), ("metasploit", "Metasploit", ""),
                  ("owasp", "OWASP", ""), (None, "IDA Pro", "IDA"), (None, "Ghidra", "Gh"),
                  (None, "Frida", "Fr"), (None, "Wazuh", "Wz"), ("tryhackme", "TryHackMe", "")]),
    ("code", [("python", "Python", ""), ("c", "C", ""), ("gnubash", "Bash", ""), ("openjdk", "Java", ""),
              ("kotlin", "Kotlin", ""), ("swift", "Swift", ""), ("typescript", "TypeScript", ""),
              ("nextdotjs", "Next.js", ""), (None, "x86 asm", "asm")]),
    ("systems", [("archlinux", "Arch", ""), ("kalilinux", "Kali", ""), ("android", "Android", ""),
                 ("ios", "iOS", ""), ("docker", "Docker", ""), ("virtualbox", "VirtualBox", ""),
                 ("qemu", "QEMU", ""), (None, "GNS3", "G3"), ("git", "Git", "")]),
]

W, PAD, TILE_W, TILE_H, GAP, ICON = 640, 27, 58, 62, 8, 24
ROW_LABEL_H, ROW_GAP, TOP = 22, 14, 46
INK, DIM, MEM, ACC = "#F1EAE3", "#998E86", "#9DB6DA", "#F2C9A8"
BG, BAR, TILE, EDGE, DOT = "#0D0B0A", "#171312", "#171312", "#2A2321", "#3E3532"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
INTRO_MS, STAGGER_MS, SWEEP_S = 300, 45, 7


def readable(hex_colour):
    """Brand colours that vanish on a dark card (black logos) fall back to the ink colour."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return INK if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.22 else "#" + hex_colour


def icon_path(slug):
    return re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text()).group(1)


def tile(x, y, k, total, slug, label, mono):
    begin = INTRO_MS + k * STAGGER_MS
    p = 0.05 + 0.8 * k / total
    sweep = (f'<animate attributeName="stroke" values="{EDGE};{EDGE};{ACC};{EDGE};{EDGE}" '
             f'keyTimes="0;{p:.3f};{p + 0.02:.3f};{p + 0.07:.3f};1" dur="{SWEEP_S}s" '
             f'begin="{INTRO_MS + total * STAGGER_MS + 800}ms" repeatCount="indefinite"/>')
    cx = x + TILE_W / 2
    if slug:
        scale = ICON / 24
        art = (f'<path transform="translate({cx - ICON / 2:.1f} {y + 11}) scale({scale})" '
               f'fill="{readable(META[slug]["hex"])}" d="{icon_path(slug)}"/>')
    else:
        art = (f'<text x="{cx:.1f}" y="{y + 30}" text-anchor="middle" font-family="{MONO}" '
               f'font-size="17" font-weight="700" fill="{ACC}">{escape(mono)}</text>')
    return (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin}ms" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 8;0 0" '
            f'dur="320ms" begin="{begin}ms" fill="freeze"/>'
            f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="10" fill="{TILE}" stroke="{EDGE}">{sweep}</rect>'
            f'{art}<text x="{cx:.1f}" y="{y + TILE_H - 9}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="9" fill="{DIM}">{escape(label)}</text></g>')


def build():
    total = sum(len(items) for _, items in ROWS)
    out, y, k = [], TOP, 0
    for name, items in ROWS:
        out.append(f'<text x="{PAD}" y="{y + 12}" font-family="{MONO}" font-size="12" fill="{MEM}">{escape(name)}</text>')
        y += ROW_LABEL_H
        for i, (slug, label, mono) in enumerate(items):
            out.append(tile(PAD + i * (TILE_W + GAP), y, k, total, slug, label, mono))
            k += 1
        y += TILE_H + ROW_GAP
    h = y + 8
    names = ", ".join(label for _, items in ROWS for _, label, _ in items)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="t d">
<title id="t">Toolbox</title>
<desc id="d">Tools and languages: {escape(names)}.</desc>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="{BAR}"/>
<circle cx="20" cy="16" r="5" fill="{DOT}"/><circle cx="37" cy="16" r="5" fill="{DOT}"/><circle cx="54" cy="16" r="5" fill="{DOT}"/>
<text x="{W / 2}" y="20" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{DIM}">fadigaa@insat: ~/toolbox</text>
{chr(10).join(out)}
</svg>
'''


if __name__ == "__main__":
    dest = HERE.parent / "assets" / "toolbox.svg"
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest}")
