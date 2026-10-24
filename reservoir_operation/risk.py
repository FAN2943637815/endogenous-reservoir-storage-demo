"""Finite-path drought-risk calculations for the public two-stage example."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .system import Reservoir, Stage


def check_probabilities(probabilities: list[float] | tuple[float, ...]) -> None:
    if not probabilities or any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError("Probabilities must be finite and nonnegative.")
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError("Probabilities must sum to one.")


@dataclass(frozen=True)
class RiskThresholds:
    expected_shortage: float = 0.10
    critical_probability: float = 0.10
    cvar: float = 0.20

    def validate(self) -> None:
        if any(not math.isfinite(v) or v <= 0 for v in
               (self.expected_shortage, self.critical_probability, self.cvar)):
            raise ValueError("Risk thresholds must be finite and positive.")


@dataclass(frozen=True)
class RiskMetrics:
    expected_shortage: float
    critical_probability: float
    cvar: float
    physical_violation_probability: float
    path_count: int


def weighted_cvar(losses: list[float], probabilities: list[float], beta: float = 0.90) -> float:
    """Average of the worst 1-beta probability mass, with fractional boundary."""
    if len(losses) != len(probabilities) or not 0 <= beta < 1:
        raise ValueError("Loss/probability dimensions or beta are invalid.")
    check_probabilities(probabilities)
    if any(not math.isfinite(loss) or loss < 0 for loss in losses):
        raise ValueError("Losses must be finite and nonnegative.")
    remaining = 1.0 - beta
    total = 0.0
    for loss, probability in sorted(zip(losses, probabilities), reverse=True):
        taken = min(remaining, probability)
        total += taken * loss
        remaining -= taken
        if remaining <= 1e-12:
            break
    return total / (1.0 - beta)


def evaluate_risk(
    reservoir: Reservoir,
    start_storage: float,
    current_stage: Stage,
    current_inflows: tuple[float, ...],
    target: float,
    posterior: list[float],
    transitions: list[list[list[float]]],
    future_inflows: list[tuple[float, ...]],
    future_stages: list[Stage],
    beta: float = 0.90,
) -> RiskMetrics:
    """Enumerate h period states from current posterior; h=1+future stages.

    The current supply uses each current inflow state. In line with the
    manuscript's path initialization, the following period starts at the
    candidate target. Future supply uses an explicit teaching rule that
    releases only water above critical storage.
    """
    check_probabilities(posterior)
    current_stage.validate(reservoir)
    k = len(posterior)
    if (len(current_inflows) != k or len(transitions) != len(future_stages)
            or len(future_inflows) != len(future_stages)):
        raise ValueError("Current states and future window must align.")
    if (not math.isfinite(start_storage) or start_storage < reservoir.dead_storage
            or not math.isfinite(target)
            or not reservoir.dead_storage <= target <= current_stage.upper_storage
            or not 0 <= beta < 1):
        raise ValueError("Invalid storage, target, or beta.")
    if any(q < 0 or not math.isfinite(q) for q in current_inflows):
        raise ValueError("Current inflows must be finite and nonnegative.")
    for stage, inflows, matrix in zip(future_stages, future_inflows, transitions):
        stage.validate(reservoir)
        if len(inflows) != k or any(q < 0 or not math.isfinite(q) for q in inflows):
            raise ValueError("Future inflows must be finite and nonnegative.")
        if len(matrix) != k or any(len(row) != k for row in matrix):
            raise ValueError("Transition matrix dimensions do not match states.")
        for row in matrix:
            check_probabilities(row)

    losses: list[float] = []
    probabilities: list[float] = []
    hits: list[bool] = []
    physical: list[bool] = []

    def visit(
        depth: int, previous_state: int, storage: float, probability: float,
        shortage: float, demand: float, hit: bool, violation: bool
    ) -> None:
        if depth == len(future_stages):
            losses.append(shortage / demand)
            probabilities.append(probability)
            hits.append(hit)
            physical.append(violation)
            return
        stage = future_stages[depth]
        for next_state, conditional in enumerate(transitions[depth][previous_state]):
            if conditional == 0:
                continue
            water = storage + future_inflows[depth][next_state] - stage.loss
            below_dead = water < reservoir.dead_storage - 1e-9
            supply = min(stage.demand, max(0.0, water - stage.critical_storage))
            end = min(stage.upper_storage, water - supply)
            visit(
                depth + 1, next_state, end, probability * conditional,
                shortage + stage.demand - supply, demand + stage.demand,
                hit or end < stage.critical_storage - 1e-9,
                violation or below_dead,
            )

    next_critical = (future_stages[0].critical_storage if future_stages
                     else current_stage.critical_storage)
    for state, probability in enumerate(posterior):
        if probability == 0:
            continue
        water = start_storage + current_inflows[state] - current_stage.loss
        supply = min(current_stage.demand, max(0.0, water - target))
        visit(
            0, state, target, probability, current_stage.demand - supply,
            current_stage.demand, target < next_critical - 1e-9,
            water < reservoir.dead_storage - 1e-9,
        )
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError("Enumerated path probabilities do not sum to one.")
    return RiskMetrics(
        expected_shortage=sum(p * loss for p, loss in zip(probabilities, losses)),
        critical_probability=sum(p for p, hit in zip(probabilities, hits) if hit),
        cvar=weighted_cvar(losses, probabilities, beta),
        physical_violation_probability=sum(p for p, flag in zip(probabilities, physical) if flag),
        path_count=len(probabilities),
    )


def is_feasible(metrics: RiskMetrics, limits: RiskThresholds) -> bool:
    limits.validate()
    return (metrics.physical_violation_probability <= 1e-12
            and metrics.expected_shortage <= limits.expected_shortage + 1e-12
            and metrics.critical_probability <= limits.critical_probability + 1e-12
            and metrics.cvar <= limits.cvar + 1e-12)


def maximum_standardized_violation(metrics: RiskMetrics, limits: RiskThresholds) -> float:
    """Manuscript fallback Eq. fallback_solution for the three risk ratios."""
    limits.validate()
    return max(
        0.0,
        metrics.expected_shortage / limits.expected_shortage - 1,
        metrics.critical_probability / limits.critical_probability - 1,
        metrics.cvar / limits.cvar - 1,
    )
