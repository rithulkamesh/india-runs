"""Career analyzer — analyze career trajectory, company types, and progression."""

from src.ranker.config import JDConfig
from src.ranker.title_classifier import classify_title, is_ai_ml_title


CONSULTING_COMPANIES_LOWER = {c.lower() for c in JDConfig().consulting_companies}

PRODUCT_COMPANY_SIGNALS_LOWER = {c.lower() for c in JDConfig().product_company_signals}


def analyze_career(career_history: list[dict]) -> dict:
    """Analyze a candidate's career history.

    Returns:
        total_duration_months: Total career duration
        num_companies: Number of distinct companies
        num_roles: Number of roles
        has_product_company: Whether any role was at a product company
        has_consulting_only: Whether ALL roles were at consulting firms
        product_company_months: Months at product companies
        consulting_months: Months at consulting firms
        ai_ml_role_months: Months in AI/ML roles
        avg_role_duration: Average months per role
        title_progression_score: 0-1 score for upward career trajectory
        short_tenure_count: Number of roles < 18 months
        current_role_duration: Duration of current role
        companies: List of company names
        industries: List of industries
    """
    if not career_history:
        return {
            "total_duration_months": 0,
            "num_companies": 0,
            "num_roles": 0,
            "has_product_company": False,
            "has_consulting_only": True,
            "product_company_months": 0,
            "consulting_months": 0,
            "ai_ml_role_months": 0,
            "avg_role_duration": 0,
            "title_progression_score": 0.0,
            "short_tenure_count": 0,
            "current_role_duration": 0,
            "companies": [],
            "industries": [],
        }

    total_duration = 0
    product_months = 0
    consulting_months = 0
    ai_ml_months = 0
    companies = set()
    industries = set()
    role_durations = []
    short_tenures = 0
    current_duration = 0
    title_tiers = []

    for role in career_history:
        dur = role.get("duration_months", 0)
        total_duration += dur
        role_durations.append(dur)

        company_lower = role.get("company", "").lower()
        industry_lower = role.get("industry", "").lower()
        title = role.get("title", "")

        companies.add(company_lower)
        industries.add(industry_lower)

        if role.get("is_current"):
            current_duration = dur

        if industry_lower in PRODUCT_COMPANY_SIGNALS_LOWER:
            product_months += dur
        elif company_lower in CONSULTING_COMPANIES_LOWER:
            consulting_months += dur

        if is_ai_ml_title(title):
            ai_ml_months += dur

        if dur < 18 and not role.get("is_current"):
            short_tenures += 1

        tier_score = {
            "senior_ai": 5, "senior_swe_ml": 5, "senior_ml_engineer": 5,
            "senior_data_scientist": 5, "lead": 5, "principal": 5, "staff": 5,
            "ai_engineer": 4, "ai_research": 4, "data_scientist": 4,
            "junior_ml": 2, "adjacent_tech": 2, "non_tech": 1, "unknown": 1,
        }
        title_class = classify_title(title)
        score = 1
        for key, val in tier_score.items():
            if key in title_class:
                score = val
                break
        title_tiers.append(score)

    avg_duration = sum(role_durations) / len(role_durations) if role_durations else 0

    progression = 0.0
    if len(title_tiers) >= 2:
        increasing = sum(1 for i in range(1, len(title_tiers)) if title_tiers[i] >= title_tiers[i - 1])
        progression = increasing / (len(title_tiers) - 1)

    has_product = product_months > 0
    only_consulting = len(industries) == 1 and "it services" in industries

    return {
        "total_duration_months": total_duration,
        "num_companies": len(companies),
        "num_roles": len(career_history),
        "has_product_company": has_product,
        "has_consulting_only": only_consulting,
        "product_company_months": product_months,
        "consulting_months": consulting_months,
        "ai_ml_role_months": ai_ml_months,
        "avg_role_duration": avg_duration,
        "title_progression_score": progression,
        "short_tenure_count": short_tenures,
        "current_role_duration": current_duration,
        "companies": list(companies),
        "industries": list(industries),
    }


def compute_career_fit_score(career_analysis: dict, yoe: float) -> dict:
    """Compute career fit scores for ranking."""
    ca = career_analysis
    total = max(ca["total_duration_months"], 1)

    product_ratio = ca["product_company_months"] / total
    ai_ratio = ca["ai_ml_role_months"] / total

    if ca["has_consulting_only"]:
        product_penalty = 0.3
    elif product_ratio > 0.6:
        product_penalty = 1.0
    elif product_ratio > 0.3:
        product_penalty = 0.75
    else:
        product_penalty = 0.5

    if ai_ratio > 0.7:
        ai_role_score = 1.0
    elif ai_ratio > 0.5:
        ai_role_score = 0.85
    elif ai_ratio > 0.3:
        ai_role_score = 0.65
    else:
        ai_role_score = 0.3

    short_tenure_penalty = 1.0 - (ca["short_tenure_count"] * 0.1)
    short_tenure_penalty = max(short_tenure_penalty, 0.5)

    progression = ca["title_progression_score"]

    yoe_ratio = 0.0
    yoe_min, yoe_max = 4.0, 12.0
    if yoe_min <= yoe <= yoe_max:
        yoe_ratio = 1.0
        ideal_min, ideal_max = 5.0, 9.0
        if ideal_min <= yoe <= ideal_max:
            yoe_ratio = 1.0
        elif yoe < ideal_min:
            yoe_ratio = 0.7 + 0.3 * ((yoe - yoe_min) / (ideal_min - yoe_min))
        else:
            yoe_ratio = 0.7 + 0.3 * ((yoe_max - yoe) / (yoe_max - ideal_max))
    elif yoe < yoe_min:
        yoe_ratio = max(0.2, (yoe / yoe_min) * 0.7)
    else:
        yoe_ratio = max(0.2, 0.5 - 0.3 * min((yoe - yoe_max) / 10.0, 1.0))

    return {
        "product_company_score": product_penalty,
        "ai_role_ratio": ai_ratio,
        "ai_role_score": ai_role_score,
        "short_tenure_penalty": short_tenure_penalty,
        "title_progression": progression,
        "yoe_score": yoe_ratio,
        "career_composite": (
            0.35 * product_penalty
            + 0.30 * ai_role_score
            + 0.10 * short_tenure_penalty
            + 0.15 * progression
            + 0.10 * yoe_ratio
        ),
    }
