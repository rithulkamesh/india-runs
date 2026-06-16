import sys
import threading
from pathlib import Path

import orjson
from fastapi import APIRouter, HTTPException, Request

sys.path.insert(0, ".")

from src.ranker.config import JDConfig
from src.ranker.pipeline import run_pipeline
from api.adapters import ranked_from_pipeline

router = APIRouter(prefix="/api")

_TOP_K = 25
_RANKING_ID = "rank-001"
_lock = threading.Lock()
# On-disk cache so the ~8s pipeline runs once ever, not on every boot.
_CACHE_PATH = Path(__file__).resolve().parents[2] / ".ranking_cache.json"


def _read_cache(expected_count: int) -> dict | None:
    try:
        blob = orjson.loads(_CACHE_PATH.read_bytes())
        if blob.get("count") == expected_count:
            return blob["ranking"]
    except (FileNotFoundError, KeyError, ValueError):
        pass
    return None


def _write_cache(count: int, ranking: dict) -> None:
    try:
        _CACHE_PATH.write_bytes(orjson.dumps({"count": count, "ranking": ranking}))
    except OSError as exc:  # pragma: no cover
        print(f"Ranking cache write failed: {exc}")


def _compute(state) -> dict:
    cfg = JDConfig()
    results = run_pipeline(state.candidates, top_k=_TOP_K, config=cfg)
    index = state.id_index
    max_skill = max((r.get("features", {}).get("skill_match_score", 0) or 0) for r in results) or 1.0
    ranked = [ranked_from_pipeline(r, index.get(r["candidate_id"], {}), max_skill) for r in results]

    return {
        "id": _RANKING_ID,
        "jobId": "jd-default",
        "jobTitle": cfg.title,
        "jobDescription": (
            f"{cfg.company} · {cfg.yoe_range[0]:.0f}–{cfg.yoe_range[1]:.0f} yrs · "
            f"must-have: {', '.join(cfg.must_have_skills[:5])}."
        ),
        "criteria": {
            "requiredSkills": list(cfg.must_have_skills[:8]),
            "preferredSkills": list(cfg.nice_to_have_skills[:6]),
            "minExperience": int(cfg.yoe_range[0]),
            "maxExperience": int(cfg.yoe_range[1]),
            "location": ", ".join(cfg.location_preference[:3]),
            "remote": "remote" in [m.lower() for m in cfg.preferred_work_mode],
        },
        "status": "completed",
        "createdAt": "2024-11-24T14:22:11Z",
        "completedAt": "2024-11-24T14:22:14Z",
        "results": ranked,
        "pipelineSteps": [
            {"name": "Honeypot Detection", "status": "completed", "duration": None, "details": "Impossible-profile filtering"},
            {"name": "Feature Computation", "status": "completed", "duration": None, "details": "30-feature engine"},
            {"name": "Scoring", "status": "completed", "duration": None, "details": "5-signal weighted LTR"},
            {"name": "Reasoning", "status": "completed", "duration": None, "details": "Per-candidate explanation"},
        ],
    }


def get_or_build(state) -> dict:
    """Return the ranking from memory → disk cache → (last resort) recompute."""
    cached = getattr(state, "_ranking", None)
    if cached is not None:
        return cached
    with _lock:
        cached = getattr(state, "_ranking", None)
        if cached is not None:
            return cached
        count = len(state.candidates)
        cached = _read_cache(count)
        if cached is None:
            cached = _compute(state)
            _write_cache(count, cached)
        state._ranking = cached
        return cached


def warm(state) -> None:
    """Precompute the ranking off the request path (called at startup)."""
    try:
        get_or_build(state)
    except Exception as exc:  # pragma: no cover - warming must never crash boot
        print(f"Ranking warm-up failed: {exc}")


@router.get("/rankings")
def list_rankings(request: Request) -> list[dict]:
    return [get_or_build(request.app.state)]


@router.get("/rankings/{ranking_id}")
def get_ranking(request: Request, ranking_id: str) -> dict:
    ranking = get_or_build(request.app.state)
    if ranking_id != ranking["id"]:
        raise HTTPException(status_code=404, detail=f"Ranking {ranking_id} not found")
    return ranking


@router.get("/rankings/{ranking_id}/results")
def get_ranking_results(request: Request, ranking_id: str) -> list[dict]:
    return get_ranking(request, ranking_id)["results"]
