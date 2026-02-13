"""Core service logic for a minimal target product ranking flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain import Candidate, normalize_score


@dataclass
class RankedCandidate:
    candidate_id: str
    score: float


class CandidateRanker:
    """Rank candidates using a weighted relevance-confidence score."""

    def __init__(self, *, relevance_weight: float = 0.7, confidence_weight: float = 0.3):
        total = relevance_weight + confidence_weight
        if total <= 0:
            raise ValueError("weights must sum to > 0")
        self.relevance_weight = relevance_weight / total
        self.confidence_weight = confidence_weight / total

    def score(self, candidate: Candidate) -> float:
        value = (
            self.relevance_weight * candidate.relevance
            + self.confidence_weight * candidate.confidence
        )
        return normalize_score(value)

    def rank(self, candidates: Iterable[Candidate]) -> list[RankedCandidate]:
        ranked = [
            RankedCandidate(candidate_id=c.candidate_id, score=self.score(c))
            for c in candidates
        ]
        ranked.sort(key=lambda item: (-item.score, item.candidate_id))
        return ranked

