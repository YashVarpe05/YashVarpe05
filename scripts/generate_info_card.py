#!/usr/bin/env python3
"""Build the personalized terminal-style profile information card."""

from __future__ import annotations

import html
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "profile" / "info-card.svg"
STATIC = bool(os.environ.get("STATIC"))

WIDTH = 500
HEIGHT = 400
PAD = 20
KEY_X = PAD
VALUE_X = 118
LINE_HEIGHT = 20.5

ROWS = [
    ("host",),
    ("kv", "Role", "Full Stack + Web3 Developer"),
    ("kv", "Learning", "DevOps, AWS, Kubernetes"),
    ("kv", "Speaking", "India FOSS 2025"),
    ("gap",),
    ("section", "Stack"),
    ("kv", "Frontend", "React, Next.js, Tailwind CSS"),
    ("kv", "Backend", "Node.js, Express, MongoDB, SQL"),
    ("kv", "Web3", "Solidity, Thirdweb, Blockchain"),
    ("kv", "DevOps", "Docker, Git, Linux, CI/CD"),
    ("gap",),
    ("section", "Highlights"),
    ("bullet", "Winner · I Love Hackathon, Pune Web3"),
    ("bullet", "FOSS Club Lead + CODEX Web Dev Lead"),
    ("bullet", "Organizer · CODELITE 2.0 Hackathon"),
]


def animate(content: str, index: int) -> str:
    if STATIC:
        return f"<g>{content}</g>"
    delay = 0.15 + index * 0.06
    return (
        f'<g opacity="0" transform="translate(0,5)">{content}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur=".4s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></g>'
    )


def render() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<title id="title">Yash Varpe profile summary</title>',
        '<desc id="desc">Yash Varpe\'s role, technical stack, and community highlights in a terminal-style card.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>',
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>',
        '<line x1="0" y1="30" x2="500" y2="30" stroke="#30363d"/>',
    ]
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{18 + index * 15}" cy="15" r="4.5" fill="{color}"/>')
    parts.append(
        '<text x="250" y="19" fill="#7d8590" font-size="11" text-anchor="middle">'
        'yash@github: ~$ neofetch</text>'
    )

    y = 60.0
    for index, row in enumerate(ROWS):
        kind = row[0]
        if kind == "gap":
            y += LINE_HEIGHT * 0.5
            continue
        if kind == "host":
            content = (
                f'<text x="{KEY_X}" y="{y}" font-size="14" font-weight="700">'
                '<tspan fill="#3fb950">yash</tspan><tspan fill="#7d8590">@</tspan>'
                '<tspan fill="#22d3ee">github</tspan></text>'
                f'<line x1="120" y1="{y - 4}" x2="480" y2="{y - 4}" stroke="#30363d"/>'
            )
        elif kind == "section":
            title = html.escape(row[1])
            content = (
                f'<text x="{KEY_X}" y="{y}" fill="#58a6ff" font-size="12.5" font-weight="700">— {title}</text>'
                f'<line x1="{KEY_X + 30 + len(row[1]) * 8}" y1="{y - 4}" x2="480" y2="{y - 4}" stroke="#30363d"/>'
            )
        elif kind == "kv":
            key, value = html.escape(row[1]), html.escape(row[2])
            content = (
                f'<text x="{KEY_X}" y="{y}" fill="#ffa657" font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{VALUE_X}" y="{y}" fill="#c9d1d9" font-size="12.5">{value}</text>'
            )
        else:
            value = html.escape(row[1])
            content = (
                f'<circle cx="{KEY_X + 3}" cy="{y - 4}" r="2.5" fill="#3fb950"/>'
                f'<text x="{KEY_X + 14}" y="{y}" fill="#c9d1d9" font-size="12.5">{value}</text>'
            )
        parts.append(animate(content, index))
        y += LINE_HEIGHT

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
