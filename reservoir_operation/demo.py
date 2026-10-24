"""Run the independent finite-grid reservoir operation example."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .risk import RiskThresholds
from .simulation import RollingInput, run_rolling
from .system import Reservoir, Stage


def run(output_dir: Path) -> dict[str, object]:
    """Prescribed toy probabilities; this independent demo does not claim a posterior."""
    reservoir = Reservoir(dead_storage=1.0)
    stage = Stage(demand=1.25, loss=0.05, upper_storage=10.0, critical_storage=3.0)
    inflow_states = (0.65, 1.10, 1.60)
    probabilities = [0.25, 0.50, 0.25]
    transition = [[0.65, 0.30, 0.05], [0.20, 0.60, 0.20], [0.05, 0.30, 0.65]]
    actuals = (1.05, 0.80, 0.72, 1.25, 1.50, 0.95)
    periods = [
        RollingInput(
            actual_inflow=q, stage=stage, scenario_inflows=inflow_states,
            probabilities=probabilities, transitions=[transition],
            future_inflows=[inflow_states], future_stages=[stage],
        )
        for q in actuals
    ]
    limits = RiskThresholds(expected_shortage=0.40, critical_probability=0.45, cvar=0.70)
    steps, decisions, summary = run_rolling(
        reservoir, initial_storage=6.0, periods=periods,
        nodes=tuple(float(i) for i in range(1, 11)), limits=limits,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "operation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["period", *asdict(steps[0])])
        writer.writeheader()
        writer.writerows({"period": i, **asdict(step)} for i, step in enumerate(steps, 1))
    decisions_table = [
        {
            "period": i, "chosen_target_1e8m3": decision.chosen.target_storage,
            "objective": decision.chosen.objective,
            "expected_shortage_ratio": decision.chosen.risk.expected_shortage,
            "critical_probability": decision.chosen.risk.critical_probability,
            "cvar_shortage_ratio": decision.chosen.risk.cvar,
            "risk_feasible": decision.chosen.feasible,
            "used_fallback": decision.used_fallback,
            "n_candidates": len(decision.candidates),
        }
        for i, decision in enumerate(decisions, 1)
    ]
    with (output_dir / "decisions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decisions_table[0]))
        writer.writeheader()
        writer.writerows(decisions_table)
    screening = [
        {
            "target_1e8m3": candidate.target_storage,
            "bellman_objective": candidate.objective,
            "expected_shortage_ratio": candidate.risk.expected_shortage,
            "critical_probability": candidate.risk.critical_probability,
            "cvar_shortage_ratio": candidate.risk.cvar,
            "risk_feasible": candidate.feasible,
        }
        for candidate in decisions[0].candidates
    ]
    with (output_dir / "candidate_screening.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(screening[0]))
        writer.writeheader()
        writer.writerows(screening)
    result = {
        "mode": "public_demo",
        "description": "Prescribed toy probability input and two-stage finite-grid search",
        "reservoir": asdict(reservoir),
        "stage": asdict(stage),
        "scenario_inflows_1e8m3": inflow_states,
        "probabilities": probabilities,
        "risk_thresholds": asdict(limits),
        "metrics": summary,
        "first_decision": decisions_table[0],
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/reservoir_operation"))
    args = parser.parse_args()
    result = run(args.output_dir)
    print(f"Supply reliability={result['metrics']['supply_reliability']:.4f}")
    print(f"Wrote toy operation results to {args.output_dir}")


if __name__ == "__main__":
    main()
