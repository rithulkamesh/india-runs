import sys
from typing import Any

from fastapi import APIRouter, Request

from api.models.schemas import RankRequest, RankResponse, RankedCandidate

sys.path.insert(0, ".")

from src.ranker.pipeline import run_pipeline

router = APIRouter(prefix="/api")

_pipeline_lock: Any = None


def _ensure_lock():
    global _pipeline_lock
    if _pipeline_lock is None:
        import threading
        _pipeline_lock = threading.Lock()


@router.post("/rank", response_model=RankResponse)
def rank_candidates(
    request: Request,
    body: RankRequest | None = None,
) -> RankResponse:
    _ensure_lock()
    body = body or RankRequest()
    candidates = request.app.state.candidates

    with _pipeline_lock:
        results = run_pipeline(candidates, top_k=body.top_k)

    ranked = [
        RankedCandidate(
            candidate_id=r["candidate_id"],
            rank=r["rank"],
            score=r["score"],
            reasoning=r["reasoning"],
            features=r["features"],
        )
        for r in results
    ]

    return RankResponse(total=len(ranked), results=ranked)
