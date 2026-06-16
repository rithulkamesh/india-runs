import time

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/system")

_start = time.monotonic()


def _memory_mb() -> float:
    try:
        import resource
        import sys

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes, Linux reports kilobytes.
        return round(rss / (1024 * 1024 if sys.platform == "darwin" else 1024), 1)
    except Exception:
        return 0.0


@router.get("/metrics")
def metrics(request: Request) -> dict:
    return {
        "totalCandidates": getattr(request.app.state, "candidate_count", 0),
        "uptimeSeconds": round(time.monotonic() - _start, 1),
        "memoryUsageMb": _memory_mb(),
    }
