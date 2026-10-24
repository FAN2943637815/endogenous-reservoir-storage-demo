"""Dekad-specific empirical-quantile inflow states (Appendix A)."""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass


def quantile(values: list[float], probability: float) -> float:
    if not values or not 0 <= probability <= 1:
        raise ValueError("Provide values and a probability in [0,1].")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    left = math.floor(position)
    right = math.ceil(position)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


@dataclass(frozen=True)
class StateDefinition:
    thresholds: tuple[float, ...]
    lower: float
    upper: float

    def classify(self, inflow: float) -> int:
        """One-based dry-to-wet state; exact threshold stays in lower state."""
        if not math.isfinite(inflow) or inflow < 0:
            raise ValueError("Inflow must be finite and nonnegative.")
        return bisect.bisect_left(self.thresholds, inflow) + 1

    @property
    def representatives(self) -> tuple[float, ...]:
        bounds = (self.lower, *self.thresholds, self.upper)
        return tuple((bounds[i] + bounds[i + 1]) / 2 for i in range(len(bounds) - 1))


def fit_dekad_states(
    rows: list[dict[str, object]], states: int = 5, excluded_year: int | None = None
) -> dict[int, StateDefinition]:
    """Fit each period's thresholds; omit evaluation year before fitting."""
    if states < 2:
        raise ValueError("At least two inflow states are required.")
    by_dekad: dict[int, list[float]] = {i: [] for i in range(1, 37)}
    for row in rows:
        if excluded_year is not None and int(row["year"]) == excluded_year:
            continue
        period = int(row["dekad"])
        value = float(row["inflow_1e8m3"])
        if period not in by_dekad or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid dekad or inflow volume.")
        by_dekad[period].append(value)
    if any(len(values) < states for values in by_dekad.values()):
        raise ValueError("Each dekad needs at least K training observations.")
    return {
        period: StateDefinition(
            tuple(quantile(values, m / states) for m in range(1, states)),
            min(values), max(values),
        )
        for period, values in by_dekad.items()
    }
