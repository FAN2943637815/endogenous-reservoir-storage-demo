"""Manuscript probability metrics for the public state example."""

from __future__ import annotations

import math

from .prior import check_probabilities


def ranked_probability_score(probabilities: list[float], observed_state: int) -> float:
    """Normalized RPS in Appendix D, with states numbered 1..K."""
    check_probabilities(probabilities)
    if len(probabilities) < 2 or not 1 <= observed_state <= len(probabilities):
        raise ValueError("Invalid state or probability vector.")
    cumulative = 0.0
    score = 0.0
    for k, probability in enumerate(probabilities[:-1], start=1):
        cumulative += probability
        score += (cumulative - float(observed_state <= k)) ** 2
    return score / (len(probabilities) - 1)


def kl_information_gain(prior: list[float], posterior: list[float]) -> float:
    """D_KL(posterior || prior), Eq. app_kl, in natural units."""
    check_probabilities(prior)
    check_probabilities(posterior)
    if len(prior) != len(posterior):
        raise ValueError("Probability vectors must have equal length.")
    if any(p > 0 and q == 0 for q, p in zip(prior, posterior)):
        return math.inf
    return sum(p * math.log(p / q) for q, p in zip(prior, posterior) if p > 0)


def low_inflow_auc(scores: list[float], labels: list[int]) -> float:
    """Tie-aware pairwise AUC for low-state discrimination."""
    if len(scores) != len(labels) or any(label not in (0, 1) for label in labels):
        raise ValueError("Scores and binary labels must align.")
    positive = [score for score, label in zip(scores, labels) if label == 1]
    negative = [score for score, label in zip(scores, labels) if label == 0]
    if not positive or not negative:
        raise ValueError("AUC needs both event and non-event examples.")
    return sum((a > b) + 0.5 * (a == b) for a in positive for b in negative) / (
        len(positive) * len(negative)
    )
