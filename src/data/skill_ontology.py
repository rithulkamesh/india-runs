"""Skill ontology — skill relationships, groupings, and normalization."""

from typing import Optional


SKILL_GROUPS: dict[str, list[str]] = {
    "embeddings_retrieval": [
        "embeddings", "sentence transformers", "vector search",
        "faiss", "pinecone", "qdrant", "milvus", "weaviate",
        "opensearch", "elasticsearch", "rag", "haystack",
        "semantic search", "bm25", "hybrid search",
        "cross encoder", "reranking", "retrieval",
        "langchain", "hugging face", "hugging face transformers",
        "openai embeddings", "bge", "e5",
    ],
    "ranking_evaluation": [
        "learning to rank", "ndcg", "mrr", "map",
        "information retrieval", "recommendation systems",
        "ranking", "evaluation", "a/b testing",
        "xgboost", "lightgbm", "scikit-learn",
    ],
    "llm_finetuning": [
        "fine-tuning llms", "lora", "qlora", "peft",
        "llm", "prompt engineering", "diffusion models",
        "transformers", "hugging face transformers",
    ],
    "ml_core": [
        "nlp", "deep learning", "machine learning",
        "pytorch", "tensorflow", "feature engineering",
        "data science", "statistical modeling",
        "image classification", "object detection",
        "cnn", "gan", "reinforcement learning",
        "time series", "forecasting",
    ],
    "mlops_deployment": [
        "mlops", "docker", "kubernetes", "airflow",
        "mlflow", "bentoml", "kubeflow", "spark",
        "ci/cd", "apache beam", "flask", "fastapi",
        "rest apis", "grpc", "microservices",
        "aws", "gcp", "azure",
        "tensorflow", "weights & biases",
    ],
    "data_engineering": [
        "sql", "python", "pandas", "numpy",
        "spark", "databricks", "bigquery", "snowflake",
        "kafka", "etl", "data pipelines",
        "apache flink", "apache beam",
    ],
}

SKILL_WEIGHTS: dict[str, float] = {}
for group_name, skills in SKILL_GROUPS.items():
    weight_map = {
        "embeddings_retrieval": 1.0,
        "ranking_evaluation": 0.95,
        "llm_finetuning": 0.85,
        "ml_core": 0.75,
        "mlops_deployment": 0.70,
        "data_engineering": 0.50,
    }
    w = weight_map.get(group_name, 0.5)
    for skill in skills:
        current = SKILL_WEIGHTS.get(skill, 0)
        SKILL_WEIGHTS[skill] = max(current, w)


ALIASES: dict[str, str] = {
    "fine-tuning": "fine-tuning llms",
    "sentence-transformers": "sentence transformers",
    "cv": "computer vision",
    "rl": "reinforcement learning",
    "lr": "learning to rank",
    "w&b": "weights & biases",
    "hf": "hugging face",
    "st": "sentence transformers",
}


def normalize_skill_name(name: str) -> str:
    """Normalize skill name to canonical form."""
    name_lower = name.strip().lower()
    if name_lower in ALIASES:
        return ALIASES[name_lower]
    return name_lower


def get_skill_weight(skill_name: str) -> float:
    """Get the importance weight of a skill for this JD."""
    normalized = normalize_skill_name(skill_name)
    return SKILL_WEIGHTS.get(normalized, 0.0)


def get_skill_group(skill_name: str) -> Optional[str]:
    """Get the group a skill belongs to."""
    normalized = normalize_skill_name(skill_name)
    for group_name, skills in SKILL_GROUPS.items():
        if normalized in skills:
            return group_name
    return None


def match_skills_to_jd(
    candidate_skills: list[dict],
    jd_skill_groups: dict[str, list[str]] | None = None,
) -> dict:
    """Match candidate skills against JD requirements.

    Returns dict with:
        matched_skills: list of (skill_name, weight, group)
        matched_groups: set of matched group names
        total_weight: sum of matched skill weights
        max_group_coverage: fraction of best-covered group
        skill_title_consistency: 1.0 if skills match title, <1 otherwise
    """
    groups = jd_skill_groups or SKILL_GROUPS
    matched = []
    matched_group_counts: dict[str, int] = {}
    group_sizes = {g: len(s) for g, s in groups.items()}
    total_weight = 0.0

    for skill_entry in candidate_skills:
        name = skill_entry["name"]
        normalized = normalize_skill_name(name)
        weight = get_skill_weight(name)
        group = get_skill_group(name)

        if weight > 0:
            matched.append((name, weight, group))
            total_weight += weight
            if group:
                matched_group_counts[group] = matched_group_counts.get(group, 0) + 1

    max_coverage = 0.0
    for group_name, count in matched_group_counts.items():
        size = group_sizes.get(group_name, 1)
        coverage = count / size
        max_coverage = max(max_coverage, coverage)

    groups_covered = len(matched_group_counts) / len(groups) if groups else 0

    return {
        "matched_skills": matched,
        "matched_groups": matched_group_counts,
        "total_weight": total_weight,
        "max_group_coverage": max_coverage,
        "groups_coverage_ratio": groups_covered,
    }


def compute_skill_trust_score(skill_entry: dict) -> float:
    """Compute trust score for a single skill based on proficiency, duration, endorsements.

    Trust score ranges 0-1. High proficiency + long duration + endorsements = high trust.
    Low proficiency + short duration + 0 endorsements = low trust (potential keyword stuffing).
    """
    proficiency_scores = {
        "expert": 1.0,
        "advanced": 0.85,
        "intermediate": 0.6,
        "beginner": 0.3,
    }
    prof_score = proficiency_scores.get(skill_entry.get("proficiency", ""), 0.3)

    duration_months = skill_entry.get("duration_months", 0)
    duration_score = min(duration_months / 36.0, 1.0)

    endorsements = skill_entry.get("endorsements", 0)
    endorsement_score = min(endorsements / 20.0, 1.0)

    trust = 0.4 * prof_score + 0.3 * duration_score + 0.3 * endorsement_score
    return trust
