"""Operation metrics with the manuscript's supply and shortage denominators."""

from __future__ import annotations

from .risk import weighted_cvar
from .system import StepResult


def total_shortage(steps: list[StepResult]) -> float:
    return sum(step.shortage for step in steps)


def supply_reliability(steps: list[StepResult]) -> float:
    demand = sum(step.supply + step.shortage for step in steps)
    if demand <= 0:
        raise ValueError("Total demand must be positive.")
    return sum(step.supply for step in steps) / demand


def critical_storage_hit_frequency(
    steps: list[StepResult], critical_storages: list[float]
) -> float:
    if not steps or len(steps) != len(critical_storages):
        raise ValueError("Steps and critical thresholds must align.")
    return sum(step.end_storage < threshold for step, threshold in zip(
        steps, critical_storages
    )) / len(steps)


def annual_shortage_cvar(annual_shortages: list[float], beta: float = 0.90) -> float:
    """Conditional mean above empirical VaR, Appendix D; ties remain included."""
    if not annual_shortages or not 0 <= beta < 1:
        raise ValueError("Supply annual shortages and valid beta.")
    ordered = sorted(annual_shortages)
    position = (len(ordered) - 1) * beta
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    var = ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)
    tail = [value for value in annual_shortages if value >= var]
    return sum(tail) / len(tail)


def finite_path_shortage_cvar(losses: list[float], probabilities: list[float]) -> float:
    """Optimization risk metric, distinct from annual shortage CVaR."""
    return weighted_cvar(losses, probabilities, 0.90)
