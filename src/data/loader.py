"""JSONL loader. Uses orjson when available (~2x faster), falls back to stdlib json."""

import time
from typing import Optional

try:
    import orjson

    _loads = orjson.loads
except ImportError:  # pragma: no cover
    import json

    _loads = json.loads


def load_candidates(path: str, limit: Optional[int] = None) -> list[dict]:
    """Load candidates from a JSONL file into a list of dicts."""
    candidates = []
    t0 = time.time()
    with open(path, "rb") as f:  # binary read — orjson and json both accept bytes
        for line in f:
            if not line.strip():
                continue
            candidates.append(_loads(line))
            if limit and len(candidates) >= limit:
                break
    print(f"Loaded {len(candidates)} candidates in {time.time() - t0:.2f}s")
    return candidates


def get_candidate_by_id(candidates: list[dict], candidate_id: str) -> Optional[dict]:
    """Find a candidate by ID (linear scan — fine for one-off lookups)."""
    for c in candidates:
        if c["candidate_id"] == candidate_id:
            return c
    return None


def build_id_index(candidates: list[dict]) -> dict[str, dict]:
    """Build a lookup dict from candidate_id -> candidate."""
    return {c["candidate_id"]: c for c in candidates}
