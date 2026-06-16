"""Location scorer — score candidates based on location preferences."""

from src.ranker.config import JDConfig


PREFERRED_CITIES = {c.lower() for c in JDConfig().location_preference}
PREFERRED_CITY_PARENTS = {
    "noida": "delhi ncr",
    "gurgaon": "delhi ncr",
    "gurugram": "delhi ncr",
    "delhi": "delhi ncr",
    "new delhi": "delhi ncr",
    "bangalore": "bangalore",
    "bengaluru": "bangalore",
}


def parse_location(location_str: str) -> tuple[str, str]:
    """Parse location string into (city, region) tuple.

    Handles formats like:
        'Pune, Maharashtra'
        'Noida, Uttar Pradesh'
        'Bangalore, Karnataka'
        'Mumbai'
        'Austin'
    """
    if not location_str:
        return ("", "")

    parts = [p.strip() for p in location_str.split(",")]
    city = parts[0].lower()
    region = parts[1].lower() if len(parts) > 1 else ""
    return (city, region)


def compute_location_score(candidate: dict) -> dict:
    """Compute location fit score.

    Scoring:
        1.0: Pune or Noida (primary)
        0.9: Other Tier-1 Indian cities (Bangalore, Hyderabad, Mumbai, Delhi NCR)
        0.7: Other Indian cities
        0.4: Willing to relocate but not in India
        0.2: Not in India, not willing to relocate
        0.3: Not in India, willing to relocate
    """
    profile = candidate.get("profile", {})
    location_str = profile.get("location", "")
    country = profile.get("country", "")
    signals = candidate.get("redrob_signals", {})
    willing_to_relocate = signals.get("willing_to_relocate", False)
    preferred_work_mode = signals.get("preferred_work_mode", "")

    city, region = parse_location(location_str)
    city_normalized = PREFERRED_CITY_PARENTS.get(city, city)

    score = 0.0
    location_label = ""

    if city_normalized in ("pune", "noida", "delhi ncr"):
        score = 1.0
        location_label = city_normalized.replace(" ", "/")
    elif city_normalized in PREFERRED_CITIES or city_normalized == "delhi ncr":
        score = 0.9
        location_label = city_normalized
    elif country.lower() == "india":
        score = 0.7
        location_label = "India (other)"
    elif willing_to_relocate:
        score = 0.3
        location_label = f"{city} (willing to relocate)"
    else:
        score = 0.15
        location_label = f"{city}, {country}"

    work_mode_score = 0.7
    if preferred_work_mode in ("hybrid", "flexible"):
        work_mode_score = 1.0
    elif preferred_work_mode == "onsite":
        work_mode_score = 0.8
    elif preferred_work_mode == "remote":
        work_mode_score = 0.6

    return {
        "location_score": score,
        "location_label": location_label,
        "work_mode_score": work_mode_score,
        "composite": 0.75 * score + 0.25 * work_mode_score,
    }


def compute_education_score(candidate: dict) -> dict:
    """Compute education quality score."""
    education = candidate.get("education", [])

    if not education:
        return {"tier_score": 0.3, "field_relevance": 0.3, "composite": 0.3}

    tier_values = {
        "tier_1": 1.0,
        "tier_2": 0.8,
        "tier_3": 0.5,
        "tier_4": 0.3,
        "unknown": 0.2,
    }

    relevant_fields = [
        "computer science", "data science", "artificial intelligence",
        "machine learning", "information technology", "computer engineering",
        "electrical engineering", "electronics", "mathematics",
        "statistics",
    ]

    best_tier = 0.0
    best_field = 0.0
    degree_bonus = 0.0
    has_relevant_degree = False

    for edu in education:
        tier = edu.get("tier", "unknown")
        tier_score = tier_values.get(tier, 0.2)
        best_tier = max(best_tier, tier_score)

        field = edu.get("field_of_study", "").lower()
        field_match = any(rf in field for rf in relevant_fields)
        if field_match:
            best_field = 1.0
            has_relevant_degree = True
        else:
            best_field = max(best_field, 0.3)

        degree = edu.get("degree", "").lower()
        if any(d in degree for d in ["ph.d", "m.tech", "m.s", "m.sc", "m.e", "master"]):
            degree_bonus = max(degree_bonus, 0.15)
        elif any(d in degree for d in ["b.tech", "b.e", "b.sc", "bachelor"]):
            degree_bonus = max(degree_bonus, 0.05)

    composite = 0.5 * best_tier + 0.35 * best_field + degree_bonus

    return {
        "tier_score": best_tier,
        "field_relevance": best_field,
        "degree_bonus": degree_bonus,
        "composite": composite,
    }
