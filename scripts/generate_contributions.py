#!/usr/bin/env python3
"""Render Yash's latest GitHub contributions as an animated SVG."""

from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


USERNAME = "YashVarpe05"
API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "profile" / "contributions.svg"

CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 38
TOP = 25
WIDTH = 860
HEIGHT = 160
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def fetch_data() -> dict:
    request = Request(API_URL, headers={"User-Agent": "YashVarpe05-profile-readme/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def render(data: dict) -> str:
    contributions = data["contributions"]
    if not contributions:
        raise ValueError("The contribution API returned no days")

    first_date = dt.date.fromisoformat(contributions[0]["date"])
    sunday_offset = (first_date.weekday() + 1) % 7
    positions: list[tuple[dict, int, int]] = []
    for day in contributions:
        date = dt.date.fromisoformat(day["date"])
        index = sunday_offset + (date - first_date).days
        positions.append((day, index // 7, index % 7))

    week_count = max(week for _, week, _ in positions) + 1
    max_order = max(1.0, (week_count - 1) + 6 * 0.55)
    total = data.get("total", {}).get("lastYear")
    if total is None:
        total = sum(int(day.get("count", 0)) for day in contributions)

    month_labels: list[str] = []
    seen_months: set[tuple[int, int]] = set()
    for day, week, _ in positions:
        date = dt.date.fromisoformat(day["date"])
        month_key = (date.year, date.month)
        if date.day <= 7 and month_key not in seen_months:
            seen_months.add(month_key)
            x = LEFT + week * STEP
            month_labels.append(
                f'<text class="label" x="{x}" y="15">{date.strftime("%b")}</text>'
            )

    day_labels = []
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = TOP + row * STEP + CELL - 2
        day_labels.append(f'<text class="label" x="2" y="{y}">{label}</text>')

    cells: list[str] = []
    for day, week, row in positions:
        level = max(0, min(4, int(day.get("level", 0))))
        count = int(day.get("count", 0))
        x = LEFT + week * STEP
        y = TOP + row * STEP
        delay = ((week + row * 0.55) / max_order) * 3.2
        classes = "cell active" if level else "cell"
        plural = "" if count == 1 else "s"
        title = html.escape(f'{day["date"]}: {count} contribution{plural}')
        cells.append(
            f'<g><title>{title}</title><rect class="{classes}" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" rx="2.5" fill="{COLORS[level]}" '
            f'style="animation-delay:{delay:.3f}s"/></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Yash Varpe's GitHub contribution graph</title>
<desc id="desc">{total:,} contributions in the last year, animated from left to right.</desc>
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .label {{ fill: #8b949e; font-size: 12px; font-weight: 600; }}
  .total {{ fill: #e6edf3; font-size: 14px; font-weight: 700; }}
  .cell {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .5s cubic-bezier(.2,.8,.2,1) both; }}
  @keyframes pop {{ 0% {{ opacity: 0; transform: translateY(-5px) scale(.35); }} 70% {{ opacity: 1; transform: translateY(0) scale(1.08); }} 100% {{ opacity: 1; transform: translateY(0) scale(1); }} }}
  @media (prefers-reduced-motion: reduce) {{ .cell {{ opacity: 1; animation: none; }} }}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="#0d1117"/>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="#30363d"/>
{''.join(month_labels)}
{''.join(day_labels)}
{''.join(cells)}
<text class="total" x="{LEFT}" y="{HEIGHT - 7}">{total:,} contributions in the last year</text>
</svg>'''


def main() -> None:
    try:
        data = fetch_data()
        svg = render(data)
    except (OSError, URLError, ValueError, KeyError, json.JSONDecodeError) as error:
        if OUTPUT.exists():
            print(f"Contribution refresh skipped; keeping the last SVG: {error}")
            return
        raise

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT} with {data['total']['lastYear']:,} contributions")


if __name__ == "__main__":
    main()
