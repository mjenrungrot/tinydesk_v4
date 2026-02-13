"""Domain types for the sample target product."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    """A single candidate item to score and rank."""

    candidate_id: str
    relevance: float
    confidence: float


def normalize_score(value: float) -> float:
    """Clamp scores into [0.0, 1.0] for predictable downstream behavior."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value

