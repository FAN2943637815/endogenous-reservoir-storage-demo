"""Independent synthetic prior, pseudo-hindcast, and posterior demonstration."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from .evaluation import kl_information_gain, low_inflow_auc, ranked_probability_score
from .forecast import forecast_support, pseudo_hindcast
from .posterior import bayes_update
from .prior import build_transition_matrices, prior_from_previous
from .states import fit_dekad_states


def make_synthetic_history(years: int = 16, seed: int = 20261016) -> list[dict[str, object]]:
    """Create a stand-in historical table without research data or other projects."""
    if years < 4:
        raise ValueError("At least four synthetic years are needed.")
    rng = random.Random(seed)
    anomaly = 0.0
    rows: list[dict[str, object]] = []
    for year in range(2001, 2001 + years):
        yearly = rng.gauss(0, 0.15)
        for period in range(1, 37):
            anomaly = 0.55 * anomaly + rng.gauss(0, 0.18)
            log_q = math.log(1.10) + 0.30 * math.sin(2 * math.pi * (period - 8) / 36)
            q = math.exp(log_q + yearly + anomaly)
            rows.append({"year": year, "dekad": period, "inflow_1e8m3": q})
    return rows


def run(output_dir: Path, seed: int = 20261016, sigma: float = 0.15) -> dict[str, object]:
    rows = make_synthetic_history(seed=seed)
    evaluation_year = int(rows[-1]["year"])
    definitions = fit_dekad_states(rows, states=5, excluded_year=evaluation_year)
    matrices = build_transition_matrices(rows, definitions, states=5, excluded_year=evaluation_year)
    actuals = [float(row["inflow_1e8m3"]) for row in rows if int(row["year"]) == evaluation_year]
    forecasts = pseudo_hindcast(actuals, sigma=sigma, seed=seed + 1)
    previous = float(next(row["inflow_1e8m3"] for row in rows
                          if int(row["year"]) == evaluation_year - 1 and int(row["dekad"]) == 36))
    detail: list[dict[str, object]] = []
    for period, (actual, forecast) in enumerate(zip(actuals, forecasts), start=1):
        previous_period = 36 if period == 1 else period - 1
        previous_state = definitions[previous_period].classify(previous)
        prior = prior_from_previous(matrices[period], previous_state)
        support = forecast_support(definitions[period].representatives, forecast, sigma)
        posterior = bayes_update(prior, support)
        observed_state = definitions[period].classify(actual)
        detail.append({
            "year": evaluation_year, "dekad": period,
            "actual_1e8m3": actual, "pseudo_forecast_1e8m3": forecast,
            "observed_state": observed_state, "previous_state": previous_state,
            "prior": prior, "posterior": posterior,
            "prior_rps": ranked_probability_score(prior, observed_state),
            "posterior_rps": ranked_probability_score(posterior, observed_state),
            "kl_information_gain": kl_information_gain(prior, posterior),
        })
        previous = actual
    scores = [float(row["posterior"][0]) for row in detail]
    labels = [int(row["observed_state"] == 1) for row in detail]
    result = {
        "mode": "public_demo", "seed": seed, "sigma": sigma,
        "evaluation_year": evaluation_year,
        "training_years": [2001, evaluation_year - 1],
        "mean_prior_rps": sum(float(row["prior_rps"]) for row in detail) / len(detail),
        "mean_posterior_rps": sum(float(row["posterior_rps"]) for row in detail) / len(detail),
        "mean_kl_information_gain": sum(float(row["kl_information_gain"]) for row in detail) / len(detail),
        "low_state_auc": low_inflow_auc(scores, labels) if 0 < sum(labels) < len(labels) else None,
        "first_dekad": detail[0],
        "note": "Synthetic pseudo-hindcasts are freshly generated; no archived study forecasts are included.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output_dir / "evaluation.json").write_text(json.dumps(detail, indent=2) + "\n", encoding="utf-8")
    (output_dir / "transition_dekad_1.json").write_text(
        json.dumps(matrices[1], indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/prior_posterior"))
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--sigma", type=float, default=0.15)
    args = parser.parse_args()
    result = run(args.output_dir, args.seed, args.sigma)
    print(f"Prior RPS={result['mean_prior_rps']:.4f}; posterior RPS={result['mean_posterior_rps']:.4f}")
    print(f"Wrote synthetic probability results to {args.output_dir}")


if __name__ == "__main__":
    main()
