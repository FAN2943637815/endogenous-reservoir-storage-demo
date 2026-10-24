"""Rolling execution: choose a target, observe inflow, then update storage."""

from __future__ import annotations

from dataclasses import dataclass

from .decision import Decision, choose_target
from .evaluation import critical_storage_hit_frequency, supply_reliability, total_shortage
from .risk import RiskThresholds
from .system import Reservoir, Stage, StepResult, realize


@dataclass(frozen=True)
class RollingInput:
    actual_inflow: float
    stage: Stage
    scenario_inflows: tuple[float, ...]
    probabilities: list[float]
    transitions: list[list[list[float]]]
    future_inflows: list[tuple[float, ...]]
    future_stages: list[Stage]


def run_rolling(
    reservoir: Reservoir, initial_storage: float, periods: list[RollingInput],
    nodes: tuple[float, ...], limits: RiskThresholds
) -> tuple[list[StepResult], list[Decision], dict[str, float]]:
    if not periods:
        raise ValueError("At least one rolling period is required.")
    storage = initial_storage
    steps: list[StepResult] = []
    decisions: list[Decision] = []
    for entry in periods:
        decision = choose_target(
            reservoir, storage, entry.stage, entry.scenario_inflows,
            entry.probabilities, entry.transitions, entry.future_inflows,
            entry.future_stages, nodes, limits,
        )
        step = realize(
            reservoir, entry.stage, storage, entry.actual_inflow,
            decision.chosen.target_storage,
        )
        decisions.append(decision)
        steps.append(step)
        storage = step.end_storage
    summary = {
        "total_shortage_1e8m3": total_shortage(steps),
        "supply_reliability": supply_reliability(steps),
        "critical_storage_hit_frequency": critical_storage_hit_frequency(
            steps, [entry.stage.critical_storage for entry in periods]
        ),
        "fallback_stage_fraction": sum(decision.used_fallback for decision in decisions)
        / len(decisions),
        "total_spill_1e8m3": sum(step.spill for step in steps),
        "final_storage_1e8m3": storage,
    }
    return steps, decisions, summary
