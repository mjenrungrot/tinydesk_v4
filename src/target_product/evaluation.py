"""Evaluation helpers for the sample target product."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .service import RankedCandidate


@dataclass(frozen=True)
class RankingSummary:
    count: int
    mean_score: float
    top_candidate_id: str | None


def summarize_candidates(candidates: Iterable[RankedCandidate]) -> RankingSummary:
    ranked = list(candidates)
    if not ranked:
        return RankingSummary(count=0, mean_score=0.0, top_candidate_id=None)

    mean_score = sum(c.score for c in ranked) / len(ranked)
    return RankingSummary(
        count=len(ranked),
        mean_score=mean_score,
        top_candidate_id=ranked[0].candidate_id,
    )

