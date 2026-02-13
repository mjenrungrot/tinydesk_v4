from __future__ import annotations

import pytest

from target_product.domain import Candidate, normalize_score
from target_product.service import CandidateRanker


def test_normalize_score_clamps_values() -> None:
    assert normalize_score(-0.2) == 0.0
    assert normalize_score(0.4) == 0.4
    assert normalize_score(1.4) == 1.0


def test_ranker_sorts_by_score_then_id() -> None:
    ranker = CandidateRanker(relevance_weight=0.8, confidence_weight=0.2)
    candidates = [
        Candidate("b", relevance=0.9, confidence=0.5),
        Candidate("a", relevance=0.9, confidence=0.5),
        Candidate("c", relevance=0.3, confidence=0.2),
    ]
    ranked = ranker.rank(candidates)
    assert [r.candidate_id for r in ranked] == ["a", "b", "c"]


def test_ranker_rejects_zero_total_weight() -> None:
    with pytest.raises(ValueError):
        CandidateRanker(relevance_weight=0.0, confidence_weight=0.0)

