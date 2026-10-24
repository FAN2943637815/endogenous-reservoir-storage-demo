"""Descriptive checks for demonstration synthetic runoff."""

from __future__ import annotations

import math
import statistics


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    left = math.floor(position)
    right = math.ceil(position)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


def summarize_dekad(rows: list[dict[str, object]]) -> dict[str, object]:
    """Compute volume statistics, lag-1 correlation, and low-volume spells."""
    if not rows:
        raise ValueError("At least one dekad is required")
    values = [float(row["inflow_1e8m3"]) for row in rows]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Inflow volumes must be finite and nonnegative")
    mean = statistics.fmean(values)
    std = statistics.pstdev(values)
    low_threshold = _quantile(values, 0.10)
    low_flags = [value <= low_threshold for value in values]
    run = longest = events = 0
    for flag in low_flags:
        if flag:
            if run == 0:
                events += 1
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    first, second = values[:-1], values[1:]
    if len(first) > 1 and statistics.pstdev(first) > 0 and statistics.pstdev(second) > 0:
        lag1 = statistics.correlation(first, second)
    else:
        lag1 = 0.0
    seasonal = {
        str(period): statistics.fmean(
            float(row["inflow_1e8m3"]) for row in rows if int(row["dekad"]) == period
        )
        for period in range(1, 37)
        if any(int(row["dekad"]) == period for row in rows)
    }
    return {
        "n_dekads": len(rows), "mean_1e8m3": mean, "std_1e8m3": std,
        "coefficient_of_variation": std / mean if mean else 0.0,
        "q10_1e8m3": low_threshold, "q50_1e8m3": _quantile(values, 0.50),
        "q90_1e8m3": _quantile(values, 0.90), "lag1_correlation": lag1,
        "low_dekad_events": events, "longest_low_dekad_run": longest,
        "seasonal_mean_1e8m3": seasonal,
    }
