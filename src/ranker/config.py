"""
JD Configuration — Structured requirements extracted from the Redrob AI Senior AI Engineer JD.

This encodes both the literal requirements AND the implicit signals from
"reading between the lines" sections of the JD.
"""

from dataclasses import dataclass, field


@dataclass
class JDConfig:
    title: str = "Senior AI Engineer — Founding Team"
    company: str = "Redrob AI"
    location_preference: list[str] = field(default_factory=lambda: [
        "Pune", "Noida", "Bangalore", "Bengaluru", "Hyderabad",
        "Mumbai", "Delhi", "Gurgaon", "Gurugram", "NCR",
    ])
    country_preference: list[str] = field(default_factory=lambda: ["India"])
    preferred_work_mode: list[str] = field(default_factory=lambda: [
        "hybrid", "flexible", "onsite", "remote"
    ])

    yoe_range: tuple[float, float] = (4.0, 12.0)
    yoe_ideal_range: tuple[float, float] = (5.0, 9.0)

    must_have_skills: list[str] = field(default_factory=lambda: [
        "embeddings", "retrieval", "vector database", "vector search",
        "ranking", "evaluation", "sentence-transformers", "bm25",
        "hybrid search", "ndcg", "information retrieval",
        "search", "recommendation", "production",
    ])

    strong_skills: list[str] = field(default_factory=lambda: [
        "nlp", "fine-tuning", "lora", "qlora", "peft", "llm",
        "python", "machine learning", "deep learning",
        "rag", "pinecone", "qdrant", "milvus", "weaviate", "faiss",
        "opensearch", "elasticsearch", "hugging face", "transformers",
        "feature engineering", "xgboost", "lightgbm",
        "learning to rank", "mlops", "deployment",
        "sentence transformers", "cross encoder", "reranking",
        "pytorch", "tensorflow", "scikit-learn",
        "data science", "applied ml", "applied machine learning",
        "docker", "kubernetes", "airflow", "spark",
    ])

    nice_to_have_skills: list[str] = field(default_factory=lambda: [
        "langchain", "diffusion models", "computer vision",
        "open-source", "distributed systems", "inference optimization",
        "go", "rust", "typescript", "react",
        "grpc", "rest api", "microservices",
    ])

    negative_signals_titles: list[str] = field(default_factory=lambda: [
        "marketing manager", "hr manager", "accountant", "sales executive",
        "customer support", "operations manager", "content writer",
        "graphic designer", "mechanical engineer", "civil engineer",
        "business analyst",
    ])

    ai_ml_title_keywords: list[str] = field(default_factory=lambda: [
        "ai engineer", "ai research", "ai specialist", "ml engineer",
        "machine learning", "data scientist", "nlp engineer",
        "deep learning", "applied ml", "applied scientist",
        "senior software engineer (ml)", "staff machine learning",
        "senior data scientist", "lead ai",
    ])

    adjacent_tech_titles: list[str] = field(default_factory=lambda: [
        "software engineer", "full stack developer", "backend engineer",
        "data engineer", "devops engineer", "cloud engineer",
        "frontend engineer", "mobile developer", "sre",
        "platform engineer", "site reliability",
    ])

    consulting_companies: set[str] = field(default_factory=lambda: {
        "tcs", "infosys", "wipro", "accenture", "cognizant",
        "capgemini", "hcl", "tech mahindra", "ntt data",
        "genpact", "mindtree", "ltimindtree",
    })

    product_company_signals: set[str] = field(default_factory=lambda: {
        "software", "ai/ml", "fintech", "e-commerce", "internet",
        "saas", "conversational ai", "ai services", "healthtech ai",
        "edtech", "food delivery", "transportation", "media",
        "consumer electronics", "adtech",
    })

    disqualifying_career_patterns: list[str] = field(default_factory=lambda: [
        "pure research without production",
        "only langchain/openai less than 12 months",
        "no production code in 18 months",
        "only consulting firms entire career",
        "title chasing (1.5yr switches)",
        "cv/speech/robotics without nlp/ir",
    ])

    notice_period_ideal: int = 30
    notice_period_penalty_threshold: int = 60

    weights: dict[str, float] = field(default_factory=lambda: {
        "title_career": 0.30,
        "skill_match": 0.25,
        "behavioral": 0.20,
        "experience": 0.15,
        "location_education": 0.10,
    })

    tier_cutoffs: dict[str, float] = field(default_factory=lambda: {
        "tier_1_ai_product": 1.0,
        "tier_1_ai_mixed": 0.85,
        "tier_2_adjacent_product": 0.60,
        "tier_2_ai_consulting": 0.30,
        "tier_3_other": 0.05,
        "tier_4_keyword_stuffer": 0.0,
    })
