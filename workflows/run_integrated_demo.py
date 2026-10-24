"""Generate synthetic inflow, update probabilities, and run toy reservoir decisions."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from prior_posterior.evaluation import ranked_probability_score
from prior_posterior.forecast import forecast_support, pseudo_hindcast
from prior_posterior.posterior import bayes_update
from prior_posterior.prior import build_transition_matrices, prior_from_previous
from prior_posterior.states import fit_dekad_states
from reservoir_operation.risk import RiskThresholds
from reservoir_operation.simulation import RollingInput, run_rolling
from reservoir_operation.system import Reservoir, Stage
from synthetic_inflow.diagnostics import summarize_dekad
from synthetic_inflow.generation import GenerationConfig, aggregate_dekad, generate_daily


def _csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("Cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(output_dir: Path, seed: int = 20261016) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = GenerationConfig(seed=seed, years=12)
    generated = aggregate_dekad(generate_daily(config))
    evaluation_year = config.start_year + config.years - 1
    definitions = fit_dekad_states(generated, states=5, excluded_year=evaluation_year)
    matrices = build_transition_matrices(
        generated, definitions, states=5, excluded_year=evaluation_year
    )
    eval_rows = [row for row in generated if int(row["year"]) == evaluation_year]
    actuals = [float(row["inflow_1e8m3"]) for row in eval_rows]
    forecasts = pseudo_hindcast(actuals, sigma=0.15, seed=seed + 1)
    previous = float(next(row["inflow_1e8m3"] for row in generated
                          if int(row["year"]) == evaluation_year - 1
                          and int(row["dekad"]) == 36))
    reservoir = Reservoir(dead_storage=1.0)
    stage = Stage(demand=1.20, loss=0.05, upper_storage=10.0, critical_storage=3.0)
    limits = RiskThresholds(expected_shortage=0.40, critical_probability=0.45, cvar=0.70)
    probability_rows: list[dict[str, object]] = []
    operation_inputs: list[RollingInput] = []
    for period, (actual, forecast) in enumerate(zip(actuals, forecasts), start=1):
        prior_period = 36 if period == 1 else period - 1
        previous_state = definitions[prior_period].classify(previous)
        prior = prior_from_previous(matrices[period], previous_state)
        representatives = definitions[period].representatives
        posterior = bayes_update(prior, forecast_support(representatives, forecast, 0.15))
        observed_state = definitions[period].classify(actual)
        probability_rows.append({
            "year": evaluation_year, "dekad": period,
            "actual_1e8m3": actual, "pseudo_forecast_1e8m3": forecast,
            "previous_state": previous_state, "observed_state": observed_state,
            "prior": prior, "posterior": posterior,
            "prior_rps": ranked_probability_score(prior, observed_state),
            "posterior_rps": ranked_probability_score(posterior, observed_state),
        })
        future_periods = [period % 36 + 1]
        operation_inputs.append(RollingInput(
            actual_inflow=actual, stage=stage, scenario_inflows=representatives,
            probabilities=posterior,
            transitions=[matrices[p] for p in future_periods],
            future_inflows=[definitions[p].representatives for p in future_periods],
            future_stages=[stage],
        ))
        previous = actual
    steps, decisions, metrics = run_rolling(
        reservoir, initial_storage=8.0, periods=operation_inputs,
        nodes=tuple(float(i) for i in range(1, 11)), limits=limits,
    )
    operation_rows = [
        {"year": evaluation_year, "dekad": i, **asdict(step)}
        for i, step in enumerate(steps, 1)
    ]
    decision_rows = [
        {
            "year": evaluation_year, "dekad": i,
            "target_1e8m3": decision.chosen.target_storage,
            "objective": decision.chosen.objective,
            "expected_shortage_ratio": decision.chosen.risk.expected_shortage,
            "critical_probability": decision.chosen.risk.critical_probability,
            "cvar_shortage_ratio": decision.chosen.risk.cvar,
            "risk_feasible": decision.chosen.feasible,
            "fallback": decision.used_fallback,
        }
        for i, decision in enumerate(decisions, 1)
    ]
    _csv(output_dir / "synthetic_history_dekad.csv", generated)
    _csv(output_dir / "operation.csv", operation_rows)
    _csv(output_dir / "decisions.csv", decision_rows)
    (output_dir / "probabilities.json").write_text(
        json.dumps(probability_rows, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "mode": "public_demo",
        "seed": seed,
        "training_years": [config.start_year, evaluation_year - 1],
        "evaluation_year": evaluation_year,
        "synthetic_inflow_diagnostics": summarize_dekad(generated),
        "mean_prior_rps": sum(float(row["prior_rps"]) for row in probability_rows) / 36,
        "mean_posterior_rps": sum(float(row["posterior_rps"]) for row in probability_rows) / 36,
        "operation": metrics,
        "scope": (
            "The training history is generated rather than observed; forecasts are new "
            "pseudo-hindcasts, not archived study forecasts; engineering data and the "
            "two-stage solver are illustrative."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("public-demo", "research"), default="public-demo")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/integrated"))
    parser.add_argument("--seed", type=int, default=20261016)
    args = parser.parse_args()
    if args.mode == "research":
        parser.error(
            "Research implementation unavailable: restricted observations, engineering "
            "inputs, archived pseudo-hindcasts, and the original Java solver are not supplied."
        )
    result = run(args.output_dir, args.seed)
    print(f"Public demo completed: supply reliability={result['operation']['supply_reliability']:.4f}")
    print(f"Wrote synthetic workflow results to {args.output_dir}")


if __name__ == "__main__":
    main()
