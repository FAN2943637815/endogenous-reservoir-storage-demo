"""Small, explicit Bellman search over endogenous end-storage targets."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .risk import (
    RiskMetrics, RiskThresholds, check_probabilities, evaluate_risk,
    is_feasible, maximum_standardized_violation,
)
from .system import Reservoir, Stage, engineering_candidates, realize, stage_benefit


@dataclass(frozen=True)
class Candidate:
    target_storage: float
    objective: float
    risk: RiskMetrics
    feasible: bool
    standardized_violation: float


@dataclass(frozen=True)
class Decision:
    chosen: Candidate
    candidates: tuple[Candidate, ...]
    used_fallback: bool


def terminal_storage_value(storage: float, reservoir: Reservoir, stage: Stage) -> float:
    """Manuscript Eq. terminal_value with coefficient 50."""
    width = stage.upper_storage - reservoir.dead_storage
    if width <= 0:
        return 0.0
    bounded = min(stage.upper_storage, max(reservoir.dead_storage, storage))
    return 50.0 * (bounded - reservoir.dead_storage) / width


def _continuation_value(
    reservoir: Reservoir, start: float, probabilities: list[float],
    inflows: tuple[float, ...], stage: Stage, nodes: tuple[float, ...],
    limits: RiskThresholds, beta: float,
) -> float:
    """One Bellman child stage with its own one-period risk screen."""
    choices: list[tuple[float, RiskMetrics]] = []
    for target in engineering_candidates(reservoir, stage, nodes):
        risk = evaluate_risk(
            reservoir, start, stage, inflows, target, probabilities, [], [], [], beta
        )
        if risk.physical_violation_probability > 1e-12:
            continue
        value = 0.0
        for probability, inflow in zip(probabilities, inflows):
            if probability == 0:
                continue
            try:
                step = realize(reservoir, stage, start, inflow, target)
            except ValueError:
                value = -math.inf
                break
            value += probability * (
                stage_benefit(start, inflow, target, stage)
                + terminal_storage_value(step.end_storage, reservoir, stage)
            )
        if math.isfinite(value):
            choices.append((value, risk))
    if not choices:
        return -math.inf
    feasible = [(value, risk) for value, risk in choices if is_feasible(risk, limits)]
    if feasible:
        return max(value for value, _ in feasible)
    return min(
        choices,
        key=lambda choice: (maximum_standardized_violation(choice[1], limits), -choice[0]),
    )[0]


def choose_target(
    reservoir: Reservoir,
    start_storage: float,
    current_stage: Stage,
    current_inflows: tuple[float, ...],
    posterior: list[float],
    transitions: list[list[list[float]]],
    future_inflows: list[tuple[float, ...]],
    future_stages: list[Stage],
    nodes: tuple[float, ...],
    limits: RiskThresholds,
    beta: float = 0.90,
    discount: float = 1.0,
) -> Decision:
    """Screen current targets, then solve one risk-screened Bellman child stage."""
    check_probabilities(posterior)
    k = len(posterior)
    if (len(current_inflows) != k or len(future_stages) != 1
            or len(future_inflows) != 1 or len(transitions) != 1
            or not 0 <= discount <= 1):
        raise ValueError("The public Bellman example requires two aligned periods.")
    if any(q < 0 or not math.isfinite(q) for q in current_inflows):
        raise ValueError("Current inflows must be finite and nonnegative.")
    current_stage.validate(reservoir)
    candidates: list[Candidate] = []
    for target in engineering_candidates(reservoir, current_stage, nodes):
        risk = evaluate_risk(
            reservoir, start_storage, current_stage, current_inflows, target,
            posterior, transitions, future_inflows, future_stages, beta,
        )
        objective = 0.0
        for state, (probability, inflow) in enumerate(zip(posterior, current_inflows)):
            if probability == 0:
                continue
            try:
                current_step = realize(
                    reservoir, current_stage, start_storage, inflow, target
                )
            except ValueError:
                objective = -math.inf
                break
            continuation = _continuation_value(
                reservoir, current_step.end_storage, transitions[0][state],
                future_inflows[0], future_stages[0], nodes, limits, beta,
            )
            if not math.isfinite(continuation):
                objective = -math.inf
                break
            objective += probability * (
                stage_benefit(start_storage, inflow, target, current_stage)
                + discount * continuation
            )
        candidates.append(Candidate(
            target, objective, risk, is_feasible(risk, limits) and math.isfinite(objective),
            maximum_standardized_violation(risk, limits),
        ))
    physically_valid = [
        candidate for candidate in candidates
        if candidate.risk.physical_violation_probability <= 1e-12
        and math.isfinite(candidate.objective)
    ]
    if not physically_valid:
        raise ValueError("No candidate is physically valid across the toy risk paths.")
    feasible = [candidate for candidate in physically_valid if candidate.feasible]
    if feasible:
        chosen = max(feasible, key=lambda candidate: candidate.objective)
    else:
        chosen = min(
            physically_valid,
            key=lambda candidate: (candidate.standardized_violation, -candidate.objective),
        )
    return Decision(chosen, tuple(candidates), not bool(feasible))
