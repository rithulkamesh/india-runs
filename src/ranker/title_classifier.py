"""Title classifier — assign relevance tier based on current title and career context."""

from src.ranker.config import JDConfig


TITLE_TIER_PATTERNS: list[tuple[list[str], str]] = [
    (
        [
            "senior ai engineer", "lead ai engineer", "staff ai engineer",
            "principal ai engineer",
        ],
        "senior_ai",
    ),
    (
        [
            "ai engineer", "ai specialist", "applied ml engineer",
            "applied machine learning engineer", "ml engineer",
            "machine learning engineer", "nlp engineer",
            "senior nlp engineer", "deep learning engineer",
        ],
        "ai_engineer",
    ),
    (
        [
            "ai research engineer", "ai researcher",
        ],
        "ai_research",
    ),
    (
        [
            "senior data scientist", "lead data scientist", "staff data scientist",
            "principal data scientist",
        ],
        "senior_data_scientist",
    ),
    (
        [
            "data scientist",
        ],
        "data_scientist",
    ),
    (
        [
            "senior machine learning engineer", "staff machine learning engineer",
            "lead machine learning engineer", "principal machine learning engineer",
        ],
        "senior_ml_engineer",
    ),
    (
        [
            "senior software engineer (ml)", "staff software engineer (ml)",
        ],
        "senior_swe_ml",
    ),
    (
        [
            "junior ml engineer", "ml intern",
        ],
        "junior_ml",
    ),
    (
        [
            "backend engineer", "frontend engineer", "full stack developer",
            "software engineer", "site reliability engineer", "sre",
            "platform engineer", "devops engineer", "cloud engineer",
            "data engineer",
        ],
        "adjacent_tech",
    ),
]

TITLE_TIER_SCORES: dict[str, float] = {
    "senior_ai": 1.0,
    "senior_swe_ml": 0.95,
    "senior_ml_engineer": 0.92,
    "senior_data_scientist": 0.90,
    "ai_engineer": 0.85,
    "ai_research": 0.80,
    "data_scientist": 0.70,
    "junior_ml": 0.40,
    "adjacent_tech": 0.20,
    "non_tech": 0.0,
    "unknown": 0.10,
}


def classify_title(title: str) -> str:
    """Classify a job title into a tier category."""
    title_lower = title.lower().strip()

    for patterns, tier in TITLE_TIER_PATTERNS:
        for pattern in patterns:
            if pattern in title_lower:
                return tier

    return "unknown"


def get_title_tier_score(title: str) -> float:
    """Get the base score for a title tier."""
    tier = classify_title(title)
    return TITLE_TIER_SCORES.get(tier, TITLE_TIER_SCORES["unknown"])


def is_non_tech_title(title: str) -> bool:
    """Check if title is a non-technical role (HR, Marketing, etc.)."""
    title_lower = title.lower()
    non_tech_kws = [
        "hr manager", "marketing manager", "accountant", "sales executive",
        "customer support", "operations manager", "content writer",
        "graphic designer", "mechanical engineer", "civil engineer",
        "project manager", "business analyst",
    ]
    return any(kw in title_lower for kw in non_tech_kws)


def is_ai_ml_title(title: str) -> bool:
    """Check if title is directly AI/ML related."""
    title_lower = title.lower()
    ai_kws = [
        "ai engineer", "ai research", "ai specialist", "ml engineer",
        "machine learning", "data scientist", "nlp engineer",
        "deep learning", "applied ml", "applied scientist",
    ]
    return any(kw in title_lower for kw in ai_kws)
