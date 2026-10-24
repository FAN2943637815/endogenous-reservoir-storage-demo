"""CSV/JSON/SVG output for reproducible synthetic examples."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("Cannot write an empty table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_seasonal_svg(path: Path, seasonal: dict[str, float]) -> None:
    """Generate a dependency-free SVG of mean calendar-dekad volumes."""
    values = [float(seasonal[str(i)]) for i in range(1, 37)]
    high = max(values) * 1.10 if max(values) else 1.0
    coordinates = " ".join(
        f"{50 + i * 16:.1f},{240 - value / high * 185:.1f}"
        for i, value in enumerate(values)
    )
    title = escape("Synthetic mean dekad inflow (illustrative; 10^8 m3)")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="680" height="300" viewBox="0 0 680 300">\n'
        '<rect width="680" height="300" fill="white"/>\n'
        f'<text x="50" y="28" font-family="sans-serif" font-size="16">{title}</text>\n'
        '<path d="M50 55 V240 H610" fill="none" stroke="#333"/>\n'
        f'<polyline points="{coordinates}" fill="none" stroke="#087e8b" stroke-width="3"/>\n'
        '<text x="290" y="275" font-family="sans-serif" font-size="12">Calendar dekad (1-36)</text>\n'
        '</svg>\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
