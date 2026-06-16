"""Feature engine — compute all features for a candidate."""

from src.ranker.config import JDConfig
from src.ranker.title_classifier import classify_title, get_title_tier_score, is_non_tech_title
from src.ranker.career_analyzer import analyze_career, compute_career_fit_score
from src.ranker.skill_matcher import compute_skill_match
from src.ranker.behavioral_scoring import compute_behavioral_score
from src.ranker.location_scorer import compute_location_score, compute_education_score


def compute_all_features(candidate: dict) -> dict:
    """Compute all features for a single candidate.

    Returns a dict with all feature scores and metadata needed for ranking.
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    education = candidate.get("education", [])

    title = profile.get("current_title", "")
    yoe = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")
    country = profile.get("country", "")

    title_class = classify_title(title)
    title_tier = get_title_tier_score(title)
    is_non_tech = is_non_tech_title(title)

    career_analysis = analyze_career(career)
    career_fit = compute_career_fit_score(career_analysis, yoe)

    skill_match = compute_skill_match(candidate)

    behavioral = compute_behavioral_score(signals)

    location = compute_location_score(candidate)
    education_scores = compute_education_score(candidate)

    is_keyword_stuffer = skill_match.get("is_keyword_stuffer", False)
    has_consulting_only = career_analysis.get("has_consulting_only", False)

    if is_keyword_stuffer or is_non_tech:
        title_tier = 0.0
        skill_match["effective_match_score"] = 0.0
        skill_match["title_skill_consistency"] = 0.0

    if has_consulting_only and title_tier > 0:
        title_tier *= 0.3

    summary = profile.get("summary", "").lower()
    career_descriptions = " ".join(r.get("description", "").lower() for r in career)

    retrieval_keywords = [
        "ranking", "retrieval", "search", "recommendation", "embedding",
        "vector", "bm25", "ndcg", "hybrid", "rerank",
        "candidate", "match", "scoring",
    ]
    summary_retrieval_count = sum(1 for kw in retrieval_keywords if kw in summary)
    career_retrieval_count = sum(1 for kw in retrieval_keywords if kw in career_descriptions)

    domain_match_score = min((summary_retrieval_count + career_retrieval_count) / 8.0, 1.0)

    assessment_scores = signals.get("skill_assessment_scores", {})
    avg_assessment = 0.0
    if assessment_scores:
        avg_assessment = sum(assessment_scores.values()) / len(assessment_scores)

    feature_vector = {
        "candidate_id": candidate["candidate_id"],
        "title_class": title_class,
        "title_tier": title_tier,
        "yoe": yoe,
        "current_company": company,
        "current_country": country,
        "is_non_tech": is_non_tech,
        "is_keyword_stuffer": is_keyword_stuffer,
        "has_consulting_only": has_consulting_only,

        "title_career": {
            "title_tier": title_tier,
            "product_company_score": career_fit["product_company_score"],
            "ai_role_score": career_fit["ai_role_score"],
            "ai_role_ratio": career_fit["ai_role_ratio"],
            "career_composite": career_fit["career_composite"],
            "title_progression": career_fit["title_progression"],
            "short_tenure_penalty": career_fit["short_tenure_penalty"],
        },

        "skill": {
            "matched_count": skill_match["matched_count"],
            "total_weight": skill_match["total_weight"],
            "avg_trust": skill_match["avg_trust"],
            "title_skill_consistency": skill_match["title_skill_consistency"],
            "effective_match_score": skill_match["effective_match_score"],
            "groups_coverage": skill_match["groups_coverage"],
            "endorsements_ratio": skill_match["endorsements_ratio"],
            "ai_skill_endorsements": skill_match["total_ai_skill_endorsements"],
        },

        "behavioral": {
            "composite": behavioral["composite"],
            "open_to_work": behavioral["open_to_work"],
            "response_rate": behavioral["response_rate"],
            "notice_period": behavioral["notice_period"],
            "recency": behavioral["recency"],
            "github_activity": behavioral["github_activity"],
            "verification": behavioral["verification"],
            "platform_engagement": behavioral["platform_engagement"],
        },

        "experience": {
            "yoe_score": career_fit["yoe_score"],
            "total_months": career_analysis["total_duration_months"],
            "num_companies": career_analysis["num_companies"],
            "ai_ml_role_months": career_analysis["ai_ml_role_months"],
        },

        "location_education": {
            "location_score": location["composite"],
            "location_label": location["location_label"],
            "education_score": education_scores["composite"],
            "tier_score": education_scores["tier_score"],
        },

        "domain": {
            "summary_retrieval_count": summary_retrieval_count,
            "career_retrieval_count": career_retrieval_count,
            "domain_match": domain_match_score,
            "avg_assessment": avg_assessment,
        },

        "career_analysis": career_analysis,
        "skill_match_detail": skill_match,
        "behavioral_detail": behavioral,
        "location_detail": location,
        "education_detail": education_scores,
    }

    return feature_vector
