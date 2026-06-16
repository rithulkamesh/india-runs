"""Adapters: map raw candidate dicts into the camelCase shape the React frontend
expects. Talent-DNA dimensions and the overall score come from the real feature
engine (src.ranker.features), not heuristics."""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from src.data.skill_ontology import get_skill_group
from src.ranker.features import compute_all_features

_PROF_MAP = {"beginner": 45, "intermediate": 65, "advanced": 82, "expert": 95}

# 5-signal weights from the ranker (src.ranker.config.JDConfig.weights).
_WEIGHTS = {"titleCareer": 0.30, "skillMatch": 0.25, "behavioral": 0.20, "experience": 0.15}


def _clamp(x: float) -> int:
    return max(0, min(100, round(x)))


def _slug_email(name: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "." for ch in (name or "candidate")).strip(".")
    while ".." in base:
        base = base.replace("..", ".")
    return f"{base or 'candidate'}@talent.pool"


def real_dimensions(raw: dict) -> dict[str, int]:
    """Seven Talent-DNA axes, each 0–100, derived from the real feature engine."""
    f = compute_all_features(raw)
    skill_eff = f["skill"]["effective_match_score"]  # ~0–5 in practice
    return {
        "titleCareer": _clamp(f["title_career"]["career_composite"] * 100),
        "skillMatch": _clamp(min(skill_eff / 3.0, 1.0) * 100),
        "behavioral": _clamp(f["behavioral"]["composite"] * 100),
        "experience": _clamp(f["experience"]["yoe_score"] * 100),
        "location": _clamp(f["location_education"]["location_score"] * 100),
        "education": _clamp(f["location_education"]["education_score"] * 100),
        "domain": _clamp(f["domain"]["domain_match"] * 100),
    }


def _weighted_overall(dims: dict[str, int]) -> float:
    return round(sum(dims[k] * w for k, w in _WEIGHTS.items())
                 + (dims["location"] + dims["education"]) / 2 * 0.10, 1)


def _skills(raw: dict) -> list[dict]:
    out = []
    for s in (raw.get("skills", []) or [])[:18]:
        name = s.get("name", "")
        out.append({
            "name": name,
            "category": get_skill_group(name) or "General",
            "proficiency": _PROF_MAP.get(str(s.get("proficiency", "")).lower(), 60),
            "yearsOfExperience": round(float(s.get("duration_months") or 0) / 12, 1),
        })
    return out


def _experience(raw: dict) -> list[dict]:
    return [{
        "title": h.get("title", ""),
        "company": h.get("company", ""),
        "startDate": (h.get("start_date") or "")[:7],
        "endDate": (h.get("end_date") or None) and h.get("end_date")[:7],
        "description": h.get("description", "") or "",
    } for h in raw.get("career_history", []) or []]


def _signals(raw: dict) -> list[dict]:
    sig = raw.get("redrob_signals", {}) or {}
    out = [{
        "type": "Availability",
        "value": "Open to work" if sig.get("open_to_work_flag") else "Passive",
        "confidence": round(float(sig.get("profile_completeness_score") or 60) / 100, 2),
        "source": "Redrob signals",
    }, {
        "type": "Responsiveness",
        "value": f"~{round(float(sig.get('avg_response_time_hours') or 0))}h avg reply",
        "confidence": round(float(sig.get("recruiter_response_rate") or 0), 2),
        "source": "Recruiter graph",
    }, {
        "type": "Engagement",
        "value": f"{int(sig.get('profile_views_received_30d') or 0)} views / 30d",
        "confidence": round(min(1.0, float(sig.get("search_appearance_30d") or 0) / 300), 2),
        "source": "Activity model",
    }]
    verified = [k for k in ("verified_email", "verified_phone", "linkedin_connected") if sig.get(k)]
    if verified:
        out.append({
            "type": "Verification",
            "value": ", ".join(v.replace("verified_", "").replace("_", " ").title() for v in verified),
            "confidence": round(len(verified) / 3, 2),
            "source": "Identity",
        })
    return out


def to_candidate(raw: dict, rank: int | None = None, score: float | None = None) -> dict:
    prof = raw.get("profile", {}) or {}
    dims = real_dimensions(raw)
    overall = score if score is not None else _weighted_overall(dims)
    loc = ", ".join(p for p in (prof.get("location"), prof.get("country")) if p)
    name = prof.get("anonymized_name", "")
    reasoning = (
        f"{name} is a {prof.get('current_title', 'professional')} at "
        f"{prof.get('current_company', 'their company')} with "
        f"{prof.get('years_of_experience', 0)} years of experience. "
        f"{prof.get('headline', '')}".strip()
    )

    rankings = []
    if rank is not None:
        rankings.append({
            "jobId": "jd-default",
            "jobTitle": "Senior AI Engineer — Founding Team",
            "rank": rank,
            "score": overall,
            "reasoning": reasoning,
        })

    return {
        "id": raw.get("candidate_id", ""),
        "name": name,
        "email": _slug_email(name),
        "currentRole": prof.get("current_title", ""),
        "company": prof.get("current_company", ""),
        "location": loc,
        "overallScore": overall,
        "dimensions": dims,
        "skills": _skills(raw),
        "experience": _experience(raw),
        "behavioralSignals": _signals(raw),
        "reasoning": reasoning,
        "rankings": rankings,
    }


def ranked_from_pipeline(res: dict, raw: dict, max_skill: float) -> dict:
    """Map a real run_pipeline result + its candidate into the UI RankedCandidate."""
    prof = (raw or {}).get("profile", {}) or {}
    f = res.get("features", {}) or {}
    skill = f.get("skill_match_score", 0) or 0
    return {
        "candidateId": res["candidate_id"],
        "candidateName": prof.get("anonymized_name", res["candidate_id"]),
        "currentRole": prof.get("current_title", ""),
        "company": prof.get("current_company", ""),
        "rank": res["rank"],
        "score": round(float(res.get("score", 0)) * 100, 1),
        "scoreBreakdown": {
            "skillMatch": _clamp(100 * skill / max_skill) if max_skill else 0,
            "experience": _clamp(float(f.get("career_composite", 0)) * 100),
            "culturalFit": _clamp(float(f.get("education_score", 0)) * 100),
            "growthPotential": _clamp(float(f.get("domain_match", 0)) * 100),
            "behavioralFit": _clamp(float(f.get("behavioral_composite", 0)) * 100),
        },
        "reasoning": res.get("reasoning", ""),
    }
