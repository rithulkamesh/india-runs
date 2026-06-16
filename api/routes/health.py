import time
from typing import Any

from fastapi import APIRouter, Request

from api.models.schemas import HealthResponse

router = APIRouter(prefix="/api")

_start_time = time.monotonic()


def _get_memory_mb() -> float:
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return 0.0


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        candidate_count=request.app.state.candidate_count if hasattr(request.app.state, "candidate_count") else 0,
        memory_usage_mb=round(_get_memory_mb(), 1),
        uptime_seconds=round(time.monotonic() - _start_time, 1),
        version="1.0.0",
    )


@router.get("/health/detail")
def health_detail(request: Any) -> dict:
    candidates = request.app.state.candidates
    index = request.app.state.id_index
    return {
        "status": "healthy",
        "candidate_count": len(candidates),
        "index_size": len(index),
        "memory_usage_mb": round(_get_memory_mb(), 1),
        "uptime_seconds": round(time.monotonic() - _start_time, 1),
        "version": "1.0.0",
    }
