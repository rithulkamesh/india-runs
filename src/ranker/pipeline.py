"""Main ranking pipeline — orchestrates the full ranking process."""

import heapq
import time

from src.data.loader import _loads
from src.ranker.config import JDConfig
from src.ranker.features import compute_all_features
from src.ranker.honeypot_detector import detect_honeypots, is_honeypot
from src.ranker.scoring import compute_final_score, rank_candidates
from src.ranker.reasoning_generator import generate_reasoning


def _result_row(features: dict, rank: int, score: float) -> dict:
    return {
        "candidate_id": features["candidate_id"],
        "rank": rank,
        "score": score,
        "reasoning": generate_reasoning(features, rank, score),
        "features": {
            "title_class": features["title_class"],
            "title_tier": features["title_tier"],
            "yoe": features["yoe"],
            "current_company": features["current_company"],
            "current_country": features["current_country"],
            "is_keyword_stuffer": features.get("is_keyword_stuffer", False),
            "has_consulting_only": features.get("has_consulting_only", False),
            "career_composite": features["title_career"]["career_composite"],
            "skill_match_score": features["skill"]["effective_match_score"],
            "behavioral_composite": features["behavioral"]["composite"],
            "location_score": features["location_education"]["location_score"],
            "education_score": features["location_education"]["education_score"],
            "domain_match": features["domain"]["domain_match"],
        },
    }


def run_pipeline_streaming(
    path: str,
    top_k: int = 100,
    config: JDConfig | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Single-pass ranker: stream the JSONL, keep only a top-K heap in memory.

    Peak memory is O(top_k) feature dicts instead of O(N) — megabytes, not
    gigabytes — because honeypot, feature, and score steps are per-candidate.
    """
    cfg = config or JDConfig()
    t0 = time.time()
    heap: list[tuple[float, int, dict]] = []  # min-heap of (score, seq, features)
    seq = total = honeypots = 0

    with open(path, "rb") as f:
        for line in f:
            if not line.strip():
                continue
            candidate = _loads(line)
            total += 1
            if is_honeypot(candidate):
                honeypots += 1
                continue
            feats = compute_all_features(candidate)
            score = compute_final_score(feats, cfg)
            if score > 0.01:
                if len(heap) < top_k:
                    heapq.heappush(heap, (score, seq, feats))
                    seq += 1
                elif score > heap[0][0]:
                    heapq.heapreplace(heap, (score, seq, feats))
                    seq += 1
            if limit and total >= limit:
                break

    # Final strict ordering (matches rank_candidates): score desc, ties by id asc.
    kept = sorted(((f, s) for (s, _, f) in heap), key=lambda x: (-x[1], x[0]["candidate_id"]))
    results = []
    prev = 1.0
    for i, (feats, score) in enumerate(kept):
        display = round(score, 4)
        if i > 0 and display >= prev:
            display = round(prev - 0.0001, 4)
        prev = display
        results.append(_result_row(feats, i + 1, display))

    print(f"Streamed {total} candidates ({honeypots} honeypots filtered) "
          f"-> top {len(results)} in {time.time() - t0:.2f}s")
    return results


def run_pipeline(
    candidates: list[dict],
    top_k: int = 100,
    config: JDConfig | None = None,
) -> list[dict]:
    """Run the full ranking pipeline.

    Args:
        candidates: List of candidate dicts from JSONL
        top_k: Number of top candidates to return
        config: JD config (optional, uses default if None)

    Returns:
        List of ranked candidate result dicts with rank, score, reasoning.
    """
    cfg = config or JDConfig()
    t0 = time.time()

    print(f"Pipeline: Processing {len(candidates)} candidates...")

    t1 = time.time()
    honeypot_ids = detect_honeypots(candidates)
    print(f"  Honeypot detection: {len(honeypot_ids)} flagged ({time.time()-t1:.2f}s)")

    valid_candidates = [c for c in candidates if c["candidate_id"] not in honeypot_ids]
    print(f"  Valid candidates: {len(valid_candidates)}")

    t2 = time.time()
    features_list = []
    for i, c in enumerate(valid_candidates):
        feats = compute_all_features(c)
        features_list.append(feats)
        if (i + 1) % 25000 == 0:
            print(f"  Feature computation: {i+1}/{len(valid_candidates)} ({time.time()-t2:.2f}s)")

    print(f"  Feature computation done: {len(features_list)} ({time.time()-t2:.2f}s)")

    t3 = time.time()
    ranked = rank_candidates(features_list, top_k=top_k)
    print(f"  Scoring done: {len(ranked)} candidates ({time.time()-t3:.2f}s)")

    t4 = time.time()
    results = []
    for rank, (features, score) in enumerate(ranked, start=1):
        reasoning = generate_reasoning(features, rank, score)

        results.append({
            "candidate_id": features["candidate_id"],
            "rank": rank,
            "score": score,
            "reasoning": reasoning,
            "features": {
                "title_class": features["title_class"],
                "title_tier": features["title_tier"],
                "yoe": features["yoe"],
                "current_company": features["current_company"],
                "current_country": features["current_country"],
                "is_keyword_stuffer": features.get("is_keyword_stuffer", False),
                "has_consulting_only": features.get("has_consulting_only", False),
                "career_composite": features["title_career"]["career_composite"],
                "skill_match_score": features["skill"]["effective_match_score"],
                "behavioral_composite": features["behavioral"]["composite"],
                "location_score": features["location_education"]["location_score"],
                "education_score": features["location_education"]["education_score"],
                "domain_match": features["domain"]["domain_match"],
            },
        })

    print(f"  Reasoning done: {len(results)} ({time.time()-t4:.2f}s)")
    print(f"Pipeline complete: {time.time()-t0:.2f}s total")

    return results
