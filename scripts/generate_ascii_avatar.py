#!/usr/bin/env python3
"""Turn Yash's portrait into a terminal-style animated ASCII SVG."""

from __future__ import annotations

import html
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "profile" / "yash-photo.png"
OUTPUT = ROOT / "assets" / "profile" / "ascii-avatar.svg"
STATIC = bool(os.environ.get("STATIC"))

COLS = 60
ROWS = 32
CELL_W = 6
CELL_H = 10
RAMP = " .`:-=+*cs#%@"
WIDTH = 400
HEIGHT = 400
PAD_X = (WIDTH - COLS * CELL_W) // 2
TITLEBAR = 30
ART_TOP = 37


def build_rows() -> list[str]:
    image = Image.open(SOURCE).convert("RGB")
    width, height = image.size

    # Focus on the face and upper body. Using the full portrait makes the face
    # too small to read once GitHub scales the card down.
    side = min(round(width * 0.457), round(height * 0.344))
    left = round(width * 0.282)
    top = round(height * 0.143)
    image = image.crop((left, top, left + side, top + side))

    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageEnhance.Contrast(edges).enhance(1.7)
    gray = ImageChops.darker(gray, ImageOps.invert(edges))
    gray = ImageEnhance.Contrast(gray).enhance(1.25)
    gray = ImageEnhance.Brightness(gray).enhance(1.12)
    gray = gray.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    rows: list[str] = []
    for y in range(ROWS):
        chars: list[str] = []
        for x in range(COLS):
            luminance = gray.getpixel((x, y)) / 255
            if luminance > 0.82:
                chars.append(" ")
                continue
            index = round((1 - luminance) * (len(RAMP) - 1))
            chars.append(RAMP[max(0, min(len(RAMP) - 1, index))])
        rows.append("".join(chars))
    return rows


def reveal(content: str, row: int) -> str:
    if STATIC:
        return content
    delay = row * 0.09
    row_y = ART_TOP + row * CELL_H
    return (
        f'<clipPath id="row-{row}"><rect x="{PAD_X}" y="{row_y}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{COLS * CELL_W}" begin="{delay:.2f}s" '
        f'dur=".12s" fill="freeze"/></rect></clipPath>'
        f'<g clip-path="url(#row-{row})">{content}</g>'
    )


def render(rows: list[str]) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        '<title id="title">Yash Varpe ASCII portrait</title>',
        '<desc id="desc">An animated terminal drawing generated from Yash Varpe\'s portrait.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>',
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>',
        f'<line x1="0" y1="{TITLEBAR}" x2="{WIDTH}" y2="{TITLEBAR}" stroke="#30363d"/>',
    ]
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{18 + index * 15}" cy="15" r="4.5" fill="{color}"/>')
    parts.append(
        '<text x="200" y="19" fill="#7d8590" font-size="11" text-anchor="middle" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        'yash@github: ~$ ./avatar.sh</text>'
    )

    for row, line in enumerate(rows):
        y = ART_TOP + row * CELL_H + 9
        content = (
            f'<text xml:space="preserve" x="{PAD_X}" y="{y}" fill="#c9d1d9" font-size="9.8" '
            f'textLength="{COLS * CELL_W}" lengthAdjust="spacing" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{html.escape(line)}</text>'
        )
        parts.append(reveal(content, row))

    parts.extend(
        [
            '<line x1="0" y1="365" x2="400" y2="365" stroke="#30363d"/>',
            '<text x="14" y="387" fill="#7d8590" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
            'yash@github:~$ whoami <tspan fill="#c9d1d9">Yash Varpe</tspan></text>',
            '<rect x="226" y="375" width="7" height="14" fill="#c9d1d9"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect>',
            '</svg>',
        ]
    )
    return "".join(parts)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(build_rows()), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
