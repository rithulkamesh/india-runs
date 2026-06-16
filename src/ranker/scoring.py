"""Scoring pipeline — combine features into a final score and rank candidates."""

from src.ranker.config import JDConfig


def compute_final_score(features: dict, config: JDConfig | None = None) -> float:
    """Compute the final talent match score (0-1) from feature dict."""
    cfg = config or JDConfig()
    w = cfg.weights

    if features.get("is_keyword_stuffer", False):
        return 0.0

    tc = features["title_career"]
    sk = features["skill"]
    bh = features["behavioral"]
    ex = features["experience"]
    le = features["location_education"]
    dm = features["domain"]

    title_career_score = (
        0.35 * tc["title_tier"]
        + 0.25 * tc["product_company_score"]
        + 0.25 * tc["ai_role_score"]
        + 0.15 * tc["career_composite"]
    )

    skill_score = (
        0.40 * min(sk["effective_match_score"] / 8.0, 1.0)
        + 0.25 * sk["avg_trust"]
        + 0.15 * sk["title_skill_consistency"]
        + 0.20 * sk["groups_coverage"]
    )

    behavioral_score = bh["composite"]

    experience_score = (
        0.50 * ex["yoe_score"]
        + 0.30 * tc["title_progression"]
        + 0.20 * (1.0 - min(tc["short_tenure_penalty"] - 0.5, 0.5) * 2)
    )

    location_ed_score = (
        0.55 * le["location_score"]
        + 0.45 * le["education_score"]
    )

    domain_bonus = dm["domain_match"] * 0.05

    composite = (
        w["title_career"] * title_career_score
        + w["skill_match"] * skill_score
        + w["behavioral"] * behavioral_score
        + w["experience"] * experience_score
        + w["location_education"] * location_ed_score
        + domain_bonus
    )

    title_gate = tc["title_tier"]
    skill_gate = sk["title_skill_consistency"]

    if title_gate < 0.1 and skill_gate < 0.1:
        composite *= 0.0
    elif title_gate < 0.2:
        composite *= 0.1
    elif title_gate < 0.4:
        composite *= 0.5

    if sk.get("is_keyword_stuffer", False):
        composite *= 0.0

    if features.get("has_consulting_only", False) and title_career_score > 0.3:
        composite *= 0.4

    return max(0.0, min(1.0, composite))


def rank_candidates(
    features_list: list[dict],
    top_k: int = 100,
) -> list[tuple[dict, float]]:
    """Rank candidates by final score and return top K.

    Ensures strict ordering: no equal scores, non-increasing,
    ties broken by candidate_id ascending.
    """
    scored = []
    for features in features_list:
        score = compute_final_score(features)
        if score > 0.01:
            scored.append((features, score))

    scored.sort(key=lambda x: (-x[1], x[0]["candidate_id"]))

    top = scored[:top_k]
    result = []
    prev = 1.0
    for i, (f, s) in enumerate(top):
        display = round(s, 4)
        if i > 0 and display >= prev:
            display = prev - 0.0001
            display = round(display, 4)
        prev = display
        result.append((f, display))

    return result
