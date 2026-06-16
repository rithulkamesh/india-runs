"""Reasoning generator — produce per-candidate explanation for why they were ranked."""

from src.ranker.title_classifier import classify_title


def generate_reasoning(features: dict, rank: int, score: float) -> str:
    """Generate a human-readable reasoning string for a ranked candidate.

    Must be specific to the candidate — no templating that just inserts name.
    """
    cid = features["candidate_id"]
    tc = features["title_career"]
    sk = features["skill"]
    bh = features["behavioral"]
    ex = features["experience"]
    le = features["location_education"]
    dm = features["domain"]
    ca = features.get("career_analysis", {})

    parts = []

    title_class = features.get("title_class", "unknown")
    yoe = features["yoe"]
    current_company = features.get("current_company", "")
    current_country = features.get("current_country", "")

    if title_class in ("senior_ai", "senior_swe_ml", "senior_ml_engineer"):
        seniority = "Senior"
    elif title_class in ("ai_engineer", "ai_research", "data_scientist"):
        seniority = "Mid-level"
    elif title_class == "junior_ml":
        seniority = "Junior"
    elif title_class == "adjacent_tech":
        seniority = "Adjacent"
    else:
        seniority = ""

    career_parts = []
    if current_company and current_company != "":
        career_parts.append(f"{current_company}")
    if yoe > 0:
        career_parts.append(f"{yoe:.1f}yr")

    if ca.get("has_product_company"):
        career_parts.append("product companies")
    if ca.get("has_consulting_only"):
        career_parts.append("consulting background")

    career_desc = ", ".join(filter(None, career_parts))
    if career_desc:
        parts.append(career_desc)

    top_skills = sk.get("skill_match_detail", {}).get("matched_skills", [])
    if not top_skills and "skill_match_detail" not in features:
        top_skills = [(s, w, g) for s, w, g in sk.get("matched_skills", [])[:5]]
    else:
        sm_detail = features.get("skill_match_detail", {})
        top_skills = sm_detail.get("matched_skills", [])[:5]

    if top_skills:
        skill_names = [s[0] for s in top_skills if s[0]]
        if len(skill_names) >= 3:
            parts.append(f"{len(skill_names)} relevant skills including {', '.join(skill_names[:3])}")
        elif len(skill_names) > 0:
            parts.append(f"skills: {', '.join(skill_names)}")

    ai_ml_months = ex.get("ai_ml_role_months", 0)
    if ai_ml_months > 24:
        parts.append(f"{ai_ml_months // 12}yr in AI/ML roles")
    elif ai_ml_months > 12:
        parts.append(f"{ai_ml_months}mo in AI/ML roles")

    domain = dm.get("domain_match", 0)
    if domain > 0.5:
        parts.append("direct ranking/retrieval experience")

    beh = features.get("behavioral_detail", bh)
    otw = beh.get("open_to_work", 0) if isinstance(beh, dict) else bh.get("open_to_work", 0)
    rr = beh.get("response_rate", 0) if isinstance(beh, dict) else bh.get("response_rate", 0)
    notice = ca.get("total_months", 0)

    sig_parts = []
    if isinstance(bh, dict) and bh.get("open_to_work"):
        sig_parts.append("open to work")
    if isinstance(beh, dict) and beh.get("response_rate", 0) >= 0.6:
        sig_parts.append(f"response rate {beh['response_rate']:.0%}")

    if sig_parts:
        parts.append("; ".join(sig_parts))

    if features.get("is_keyword_stuffer"):
        return f"Non-tech title with keyword-stuffed AI skills; not a genuine match."

    if features.get("has_consulting_only"):
        return (f"AI title ({current_company}) but entire career in consulting; "
                f"JD explicitly prefers product company experience.")

    if sk.get("title_skill_consistency", 1.0) < 0.3:
        return (f"Title does not match listed AI skills; "
                f"likely keyword stuffing or career mismatch.")

    location_label = le.get("location_label", "")
    if location_label and current_country == "India":
        parts.append(location_label)

    education_info = features.get("education_detail", {})
    tier = education_info.get("tier_score", 0)
    if tier >= 0.8:
        parts.append("tier-1 education")

    if not parts:
        return f"Score {score:.3f} based on composite feature scoring."

    return ". ".join(parts) + "."
