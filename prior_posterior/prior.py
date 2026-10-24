"""Seasonal-neighborhood transition counts and empirical Bayes smoothing."""

from __future__ import annotations

import math

from .states import StateDefinition


def check_probabilities(probabilities: list[float] | tuple[float, ...]) -> None:
    if not probabilities or any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError("Probabilities must be finite and nonnegative.")
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError("Probabilities must sum to one.")


def circular_distance(target: int, neighbor: int) -> int:
    if not 1 <= target <= 36 or not 1 <= neighbor <= 36:
        raise ValueError("Dekads must be in 1..36.")
    difference = abs(target - neighbor)
    return min(difference, 36 - difference)


def seasonal_weight(target: int, neighbor: int, bandwidth: float = 1.0) -> float:
    if bandwidth <= 0:
        raise ValueError("bandwidth must be positive")
    distance = circular_distance(target, neighbor)
    return math.exp(-distance * distance / (2 * bandwidth * bandwidth))


def build_transition_matrices(
    rows: list[dict[str, object]],
    definitions: dict[int, StateDefinition],
    states: int,
    excluded_year: int | None = None,
    half_width: int = 1,
    bandwidth: float = 1.0,
    smoothing_strength: float | None = None,
) -> dict[int, list[list[float]]]:
    """Estimate P_t with arrival-period weights and valid cross-year pairs.

    Eq. app_weighted_frequency counts transitions for arrival period r.
    The climatology is the column marginal of exactly these weighted counts,
    as in Eq. app_climatological_probability.
    """
    if states < 2 or not 0 <= half_width <= 17 or bandwidth <= 0:
        raise ValueError("Invalid states, neighborhood width, or bandwidth.")
    lam = float(states if smoothing_strength is None else smoothing_strength)
    if lam <= 0:
        raise ValueError("A positive smoothing strength is required.")
    observed: dict[tuple[int, int], int] = {}
    for row in rows:
        year, period = int(row["year"]), int(row["dekad"])
        if excluded_year is not None and year == excluded_year:
            continue
        key = (year, period)
        if key in observed:
            raise ValueError(f"Duplicate year/dekad: {key}")
        observed[key] = definitions[period].classify(float(row["inflow_1e8m3"]))
    result: dict[int, list[list[float]]] = {}
    for target in range(1, 37):
        counts = [[0.0] * states for _ in range(states)]
        for offset in range(-half_width, half_width + 1):
            arrival = (target - 1 + offset) % 36 + 1
            weight = seasonal_weight(target, arrival, bandwidth)
            for (year, period), current_state in observed.items():
                if period != arrival:
                    continue
                previous = (year - 1, 36) if arrival == 1 else (year, arrival - 1)
                previous_state = observed.get(previous)
                if previous_state is not None:
                    counts[previous_state - 1][current_state - 1] += weight
        total = sum(map(sum, counts))
        if total <= 0:
            raise ValueError(f"No valid transition pairs for dekad {target}")
        climatology = [sum(counts[i][j] for i in range(states)) / total for j in range(states)]
        matrix = []
        for row in counts:
            denominator = sum(row) + lam
            probabilities = [(row[j] + lam * climatology[j]) / denominator for j in range(states)]
            check_probabilities(probabilities)
            matrix.append(probabilities)
        result[target] = matrix
    return result


def prior_from_previous(matrix: list[list[float]], previous_state: int) -> list[float]:
    if not 1 <= previous_state <= len(matrix):
        raise ValueError("Previous state outside transition matrix.")
    prior = list(matrix[previous_state - 1])
    check_probabilities(prior)
    return prior


def propagate(probabilities: list[float], matrix: list[list[float]]) -> list[float]:
    """Row-vector probability propagation, manuscript Eq. posterior_propagation."""
    check_probabilities(probabilities)
    if len(matrix) != len(probabilities) or any(len(row) != len(probabilities) for row in matrix):
        raise ValueError("Matrix dimensions do not match probabilities.")
    for row in matrix:
        check_probabilities(row)
    result = [
        sum(probabilities[i] * matrix[i][j] for i in range(len(probabilities)))
        for j in range(len(probabilities))
    ]
    check_probabilities(result)
    return result
