"""Separate pseudo-hindcast and lognormal forecast likelihood modules."""

from __future__ import annotations

import math
import random


def pseudo_hindcast(actual_inflows: list[float], sigma: float, seed: int) -> list[float]:
    """Generate public synthetic forecasts: ln(Qhat)=ln(Q)+N(0,sigma^2)."""
    if sigma <= 0 or any(q <= 0 or not math.isfinite(q) for q in actual_inflows):
        raise ValueError("sigma and actual inflows must be positive and finite.")
    rng = random.Random(seed)
    return [q * math.exp(rng.gauss(0.0, sigma)) for q in actual_inflows]


def log_likelihood(representative: float, forecast: float, sigma: float) -> float:
    """Log of p(forecast | representative), Eq. forecast_likelihood."""
    if representative <= 0 or forecast <= 0 or sigma <= 0:
        raise ValueError("Positive inflows, forecasts, and sigma are required.")
    difference = math.log(forecast) - math.log(representative)
    return -math.log(forecast * sigma * math.sqrt(2 * math.pi)) - difference**2 / (2 * sigma**2)


def forecast_support(representatives: tuple[float, ...], forecast: float, sigma: float) -> list[float]:
    """Representative-value likelihood support, Eq. forecast_support_approx."""
    return [log_likelihood(q, forecast, sigma) for q in representatives]
