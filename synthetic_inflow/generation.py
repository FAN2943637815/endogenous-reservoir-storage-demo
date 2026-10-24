"""Transparent, restricted periodic autoregressive inflow generator.

The manuscript's Appendix C permits a periodic AR model after a Box--Cox
transform. This demonstration uses its lambda=0 (log) and AR(1) special
case with illustrative fixed seasonal and annual-state parameters.
It does not fit the research generator or reproduce its two scenarios.
"""

from __future__ import annotations

import calendar
import math
import random
from dataclasses import asdict, dataclass
from datetime import date, timedelta

SECONDS_PER_DAY = 86_400
VOLUME_SCALE_M3 = 100_000_000
STATE_NAMES = ("dry", "normal", "wet")
STATE_SHIFTS = (-0.24, 0.0, 0.18)
STATE_TRANSITION = ((0.60, 0.35, 0.05), (0.20, 0.60, 0.20), (0.05, 0.35, 0.60))


@dataclass(frozen=True)
class GenerationConfig:
    start_year: int = 2001
    years: int = 12
    seed: int = 20261016
    mean_flow_cms: float = 120.0
    seasonal_log_amplitude: float = 0.32
    ar_coefficient: float = 0.70
    innovation_std: float = 0.30
    log_offset_cms: float = 1.0

    def validate(self) -> None:
        if not 1900 <= self.start_year <= 9900 or self.start_year + self.years > 9999:
            raise ValueError("The requested calendar is outside supported dates.")
        if self.years < 1 or self.mean_flow_cms <= 0 or self.log_offset_cms <= 0:
            raise ValueError("years, mean_flow_cms, and log_offset_cms must be positive.")
        if not 0 <= self.ar_coefficient < 1 or self.innovation_std < 0:
            raise ValueError("AR coefficient must be in [0,1); innovation_std >= 0.")

    def parameters(self) -> dict[str, int | float]:
        return asdict(self)


def dekad_index(day: date) -> int:
    """One-based calendar dekad; the third has the month's remaining days."""
    return (day.month - 1) * 3 + (1 if day.day <= 10 else 2 if day.day <= 20 else 3)


def _draw_state(rng: random.Random, probabilities: tuple[float, ...]) -> int:
    u = rng.random()
    running = 0.0
    for state, probability in enumerate(probabilities):
        running += probability
        if u <= running:
            return state
    return len(probabilities) - 1


def generate_daily(config: GenerationConfig) -> list[dict[str, object]]:
    """Generate daily flow and exact daily volume with a seeded annual state chain."""
    config.validate()
    rng = random.Random(config.seed)
    state = _draw_state(rng, (0.25, 0.50, 0.25))
    z = 0.0
    rows: list[dict[str, object]] = []
    for year in range(config.start_year, config.start_year + config.years):
        if year > config.start_year:
            state = _draw_state(rng, STATE_TRANSITION[state])
        days = 366 if calendar.isleap(year) else 365
        current = date(year, 1, 1)
        for ordinal in range(days):
            phase = 2 * math.pi * ordinal / days
            seasonal_mean = math.log(config.mean_flow_cms + config.log_offset_cms)
            seasonal_mean += config.seasonal_log_amplitude * math.sin(phase - 0.8)
            z = config.ar_coefficient * z + rng.gauss(0.0, config.innovation_std)
            transformed = seasonal_mean + STATE_SHIFTS[state] + z
            flow = max(0.0, math.exp(transformed) - config.log_offset_cms)
            rows.append({
                "date": current.isoformat(), "year": year, "dekad": dekad_index(current),
                "annual_state": STATE_NAMES[state], "flow_cms": flow,
                "volume_1e8m3": flow * SECONDS_PER_DAY / VOLUME_SCALE_M3,
            })
            current += timedelta(days=1)
    return rows


def aggregate_dekad(daily: list[dict[str, object]]) -> list[dict[str, object]]:
    """Sum daily volumes, preserving actual third-dekad lengths."""
    grouped: dict[tuple[int, int], dict[str, object]] = {}
    for row in daily:
        key = (int(row["year"]), int(row["dekad"]))
        if key not in grouped:
            grouped[key] = {
                "year": key[0], "dekad": key[1], "days": 0,
                "annual_state": row["annual_state"], "inflow_1e8m3": 0.0,
            }
        grouped[key]["days"] = int(grouped[key]["days"]) + 1
        grouped[key]["inflow_1e8m3"] = float(grouped[key]["inflow_1e8m3"]) + float(row["volume_1e8m3"])
    return [grouped[key] for key in sorted(grouped)]


def generate_members(config: GenerationConfig, members: int) -> list[list[dict[str, object]]]:
    """Independent seeded members for a small public batch."""
    if members < 1:
        raise ValueError("members must be positive")
    return [
        aggregate_dekad(generate_daily(GenerationConfig(**(config.parameters() | {"seed": config.seed + i}))))
        for i in range(members)
    ]
