"""Skill matcher — match candidate skills to JD requirements with anti-stuffing detection."""

from src.data.skill_ontology import (
    SKILL_WEIGHTS,
    match_skills_to_jd,
    compute_skill_trust_score,
    get_skill_weight,
    normalize_skill_name,
    SKILL_GROUPS,
)
from src.ranker.title_classifier import is_ai_ml_title, classify_title


def compute_skill_match(candidate: dict) -> dict:
    """Compute comprehensive skill matching for a candidate.

    Includes anti-stuffing detection: if a non-tech title candidate
    has many "hard" AI skills, this likely indicates keyword stuffing
    and the skill match is penalized.
    """
    skills = candidate.get("skills", [])
    title = candidate.get("profile", {}).get("current_title", "")
    title_is_ai_ml = is_ai_ml_title(title)
    title_class = classify_title(title)

    jd_match = match_skills_to_jd(skills)

    matched = jd_match["matched_skills"]
    matched_count = len(matched)

    trust_scores = []
    for skill_entry in skills:
        skill_name = skill_entry["name"]
        weight = get_skill_weight(skill_name)
        if weight > 0:
            trust = compute_skill_trust_score(skill_entry)
            trust_scores.append((weight, trust))

    if trust_scores:
        avg_trust = sum(w * t for w, t in trust_scores) / sum(w for w, _ in trust_scores)
    else:
        avg_trust = 0.0

    title_skill_consistency = 1.0
    if not title_is_ai_ml and title_class == "non_tech":
        if matched_count >= 3:
            title_skill_consistency = 0.0
        elif matched_count >= 1:
            title_skill_consistency = 0.2

    elif not title_is_ai_ml and matched_count >= 8:
        title_skill_consistency = 0.3
    elif not title_is_ai_ml and matched_count >= 5:
        title_skill_consistency = 0.5

    if title_skill_consistency == 0.0:
        effective_match = 0.0
    else:
        effective_match = jd_match["total_weight"] * avg_trust * title_skill_consistency

    endorsements_total = sum(s.get("endorsements", 0) for s in skills)
    ai_skill_endorsements = sum(
        s.get("endorsements", 0)
        for s in skills
        if get_skill_weight(s["name"]) > 0
    )

    endorsements_ratio = ai_skill_endorsements / endorsements_total if endorsements_total > 0 else 0

    return {
        "matched_skills": matched,
        "matched_count": matched_count,
        "matched_groups": jd_match["matched_groups"],
        "total_weight": jd_match["total_weight"],
        "avg_trust": avg_trust,
        "title_skill_consistency": title_skill_consistency,
        "effective_match_score": effective_match,
        "groups_coverage": jd_match["groups_coverage_ratio"],
        "max_group_coverage": jd_match["max_group_coverage"],
        "total_ai_skill_endorsements": ai_skill_endorsements,
        "total_endorsements": endorsements_total,
        "endorsements_ratio": endorsements_ratio,
        "is_keyword_stuffer": title_skill_consistency == 0.0 and matched_count >= 3,
    }


def _get_max_skill_group_weight(group_name: str) -> float:
    """Get the maximum possible weight for skills in a group."""
    skills = SKILL_GROUPS.get(group_name, [])
    if not skills:
        return 0
    return sum(max(SKILL_WEIGHTS.get(s, 0) for s in skills))
