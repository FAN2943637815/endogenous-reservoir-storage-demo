"""Water balance and stage benefit in common volume units (10^8 m3)."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Reservoir:
    dead_storage: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.dead_storage) or self.dead_storage < 0:
            raise ValueError("dead_storage must be finite and nonnegative.")


@dataclass(frozen=True)
class Stage:
    demand: float
    loss: float
    upper_storage: float
    critical_storage: float

    def validate(self, reservoir: Reservoir) -> None:
        values = (self.demand, self.loss, self.upper_storage, self.critical_storage)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("Stage values must be finite.")
        if self.demand <= 0 or self.loss < 0 or not (
            reservoir.dead_storage <= self.critical_storage <= self.upper_storage
        ):
            raise ValueError("Stage demand/loss/storage bounds are invalid.")


@dataclass(frozen=True)
class StepResult:
    start_storage: float
    inflow: float
    loss: float
    target_storage: float
    supply: float
    shortage: float
    spill: float
    end_storage: float


def stage_benefit(start: float, inflow: float, target: float, stage: Stage) -> float:
    """Eq. stage_benefit: supply reward minus excess-availability penalty."""
    available = max(0.0, start + inflow - stage.loss - target)
    supply = min(stage.demand, available)
    return 100 * supply / stage.demand - 10 * max(available - stage.demand, 0) / stage.demand


def realize(
    reservoir: Reservoir, stage: Stage, start: float, inflow: float, target: float
) -> StepResult:
    """Apply a preselected target after inflow arrives; conserve all water."""
    stage.validate(reservoir)
    if not all(math.isfinite(x) for x in (start, inflow, target)):
        raise ValueError("Storage, inflow, and target must be finite.")
    if start < reservoir.dead_storage - 1e-9 or inflow < 0:
        raise ValueError("Initial storage must meet dead storage and inflow be nonnegative.")
    if not reservoir.dead_storage <= target <= stage.upper_storage:
        raise ValueError("Target is outside storage bounds.")
    water = start + inflow - stage.loss
    if water < reservoir.dead_storage - 1e-9:
        raise ValueError("Physical water deficit below dead storage.")
    supply = min(stage.demand, max(0.0, water - target))
    end_before_spill = water - supply
    spill = max(0.0, end_before_spill - stage.upper_storage)
    end = end_before_spill - spill
    return StepResult(start, inflow, stage.loss, target, supply,
                      stage.demand - supply, spill, end)


def engineering_candidates(
    reservoir: Reservoir, stage: Stage, nodes: tuple[float, ...]
) -> tuple[float, ...]:
    """Finite storage targets within the public example's engineering bounds."""
    stage.validate(reservoir)
    if not nodes:
        raise ValueError("At least one storage node is required.")
    accepted = tuple(sorted({node for node in nodes
                             if reservoir.dead_storage <= node <= stage.upper_storage}))
    if not accepted:
        raise ValueError("No storage node lies within engineering bounds.")
    return accepted
