"""Honeypot detector — identify candidates with impossible or synthetic profiles.

The dataset is synthetic with ~730 description templates shared across
100K candidates, so description-based detection is not viable.

Instead, we use per-candidate impossibility checks with very low false-positive rate.
The real filtering of keyword-stuffers and non-fits happens in the scoring pipeline,
not here.
"""

from src.ranker.title_classifier import is_non_tech_title


def detect_honeypots(candidates: list[dict]) -> set[str]:
    """Detect honeypot candidates with obviously impossible profiles.

    Conservative detection — only catches profiles that are clearly
    mathematically impossible, not just unlikely.
    """
    honeypots = set()
    for c in candidates:
        if _check_single_candidate(c):
            honeypots.add(c["candidate_id"])
    return honeypots


def _check_single_candidate(c: dict) -> bool:
    """Check for clear impossibilities."""
    profile = c.get("profile", {})
    career = c.get("career_history", [])
    skills = c.get("skills", [])

    yoe = profile.get("years_of_experience", 0)

    if career:
        total_months = sum(r.get("duration_months", 0) for r in career)
        if total_months == 0 and yoe > 0:
            return True

        for role in career:
            dur = role.get("duration_months", 0)
            if dur > 300 and not role.get("is_current"):
                return True

    expert_zero_endorse = sum(
        1 for s in skills
        if s.get("proficiency") == "expert" and s.get("endorsements", 0) == 0
    )
    if expert_zero_endorse >= 8:
        return True

    return False
