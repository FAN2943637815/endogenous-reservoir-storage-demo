"""Numerically stable statewise Bayes update."""

from __future__ import annotations

import math

from .prior import check_probabilities


def bayes_update(prior: list[float], log_support: list[float]) -> list[float]:
    """Compute normalized prior times likelihood without underflow."""
    check_probabilities(prior)
    if len(prior) != len(log_support) or any(not math.isfinite(v) for v in log_support):
        raise ValueError("Likelihood support must be finite and match prior.")
    weights = [math.log(p) + likelihood if p > 0 else -math.inf
               for p, likelihood in zip(prior, log_support)]
    maximum = max(weights)
    if maximum == -math.inf:
        raise ValueError("No state has positive prior-likelihood support.")
    scaled = [math.exp(value - maximum) if value > -math.inf else 0.0 for value in weights]
    total = sum(scaled)
    posterior = [weight / total for weight in scaled]
    check_probabilities(posterior)
    return posterior


def likelihood_only(log_support: list[float]) -> list[float]:
    """Normalize likelihoods for the forecast-only teaching benchmark."""
    if not log_support or any(not math.isfinite(v) for v in log_support):
        raise ValueError("Likelihood support must be finite.")
    maximum = max(log_support)
    scaled = [math.exp(value - maximum) for value in log_support]
    total = sum(scaled)
    result = [value / total for value in scaled]
    check_probabilities(result)
    return result
