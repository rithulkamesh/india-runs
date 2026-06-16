import sys

from fastapi import APIRouter, HTTPException, Query, Request

sys.path.insert(0, ".")

from api.adapters import to_candidate

router = APIRouter(prefix="/api")


def _matches(c: dict, term: str) -> bool:
    p = c.get("profile", {})
    if (
        term in p.get("anonymized_name", "").lower()
        or term in p.get("current_title", "").lower()
        or term in p.get("current_company", "").lower()
    ):
        return True
    return any(term in s.get("name", "").lower() for s in c.get("skills", []))


@router.get("/candidates")
def list_candidates(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: str = Query("", description="Search by name, title, company, or skill"),
) -> dict:
    candidates = request.app.state.candidates
    term = q.strip().lower()
    filtered = [c for c in candidates if _matches(c, term)] if term else candidates

    total = len(filtered)
    start = (page - 1) * limit
    page_items = filtered[start : start + limit]

    return {
        "candidates": [to_candidate(c) for c in page_items],
        "total": total,
        "page": page,
        "totalPages": max(1, (total + limit - 1) // limit),
    }


@router.get("/candidates/{candidate_id}")
def get_candidate(request: Request, candidate_id: str) -> dict:
    candidate = request.app.state.id_index.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    return to_candidate(candidate, rank=1)
