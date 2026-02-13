"""Simple target product package used for framework-driven development tests."""

from .domain import Candidate, normalize_score
from .evaluation import summarize_candidates
from .service import CandidateRanker

__all__ = [
    "Candidate",
    "CandidateRanker",
    "normalize_score",
    "summarize_candidates",
]

