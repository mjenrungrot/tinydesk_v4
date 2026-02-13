from __future__ import annotations

from target_product.domain import Candidate
from target_product.evaluation import summarize_candidates
from target_product.service import CandidateRanker


def test_summarize_candidates_non_empty() -> None:
    ranker = CandidateRanker()
    ranked = ranker.rank(
        [
            Candidate("x", relevance=0.8, confidence=0.9),
            Candidate("y", relevance=0.4, confidence=0.3),
        ]
    )
    summary = summarize_candidates(ranked)
    assert summary.count == 2
    assert summary.top_candidate_id == ranked[0].candidate_id
    assert 0.0 <= summary.mean_score <= 1.0


def test_summarize_candidates_empty() -> None:
    summary = summarize_candidates([])
    assert summary.count == 0
    assert summary.mean_score == 0.0
    assert summary.top_candidate_id is None

