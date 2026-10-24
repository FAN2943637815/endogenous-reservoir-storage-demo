"""Run the independent public synthetic inflow example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .diagnostics import summarize_dekad
from .generation import GenerationConfig, generate_members
from .outputs import write_csv, write_json, write_seasonal_svg


def run(output_dir: Path, config: GenerationConfig, members: int = 2) -> dict[str, object]:
    generated = generate_members(config, members)
    diagnostics = []
    for index, rows in enumerate(generated, start=1):
        write_csv(output_dir / f"member_{index}_dekad.csv", rows)
        diagnostic = summarize_dekad(rows)
        diagnostics.append({"member": index, **diagnostic})
        if index == 1:
            write_seasonal_svg(output_dir / "seasonal_mean.svg", diagnostic["seasonal_mean_1e8m3"])
    result = {
        "mode": "public_demo",
        "description": "Illustrative log-periodic AR(1), not the study runoff scenario generator",
        "config": config.parameters(),
        "members": diagnostics,
    }
    write_json(output_dir / "diagnostics.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/synthetic_inflow"))
    parser.add_argument("--config", type=Path, help="JSON object of GenerationConfig fields")
    parser.add_argument("--years", type=int, default=12)
    parser.add_argument("--members", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261016)
    args = parser.parse_args()
    values = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
    values.setdefault("years", args.years)
    values.setdefault("seed", args.seed)
    result = run(args.output_dir, GenerationConfig(**values), args.members)
    print(f"Wrote {len(result['members'])} synthetic members to {args.output_dir}")


if __name__ == "__main__":
    main()
