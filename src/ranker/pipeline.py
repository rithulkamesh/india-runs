"""Main ranking pipeline — orchestrates the full ranking process."""

import time
from src.ranker.config import JDConfig
from src.ranker.features import compute_all_features
from src.ranker.honeypot_detector import detect_honeypots
from src.ranker.scoring import rank_candidates
from src.ranker.reasoning_generator import generate_reasoning


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
