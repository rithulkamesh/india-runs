from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FeatureSummary(BaseModel):
    title_class: str
    title_tier: float
    yoe: float
    current_company: str
    current_country: str
    is_keyword_stuffer: bool
    has_consulting_only: bool
    career_composite: float
    skill_match_score: float
    behavioral_composite: float
    location_score: float
    education_score: float
    domain_match: float


class RankedCandidate(BaseModel):
    candidate_id: str
    rank: int
    score: float
    reasoning: str
    features: FeatureSummary


class RankRequest(BaseModel):
    top_k: int = 100


class RankResponse(BaseModel):
    total: int
    results: list[RankedCandidate]


class SkillNode(BaseModel):
    name: str
    group: str | None = None
    weight: float
    endorsements: int = 0
    proficiency: str | None = None


class CompanyNode(BaseModel):
    name: str
    role_count: int = 1
    is_current: bool = False


class RelatedCandidate(BaseModel):
    candidate_id: str
    name: str
    title: str
    shared_skills: list[str]
    shared_companies: list[str]
    similarity: float


class GraphData(BaseModel):
    candidate_id: str
    skill_nodes: list[SkillNode]
    skill_edges: list[dict[str, Any]]
    company_nodes: list[CompanyNode]
    company_edges: list[dict[str, Any]]
    related_candidates: list[RelatedCandidate]


class HealthResponse(BaseModel):
    status: str
    candidate_count: int
    memory_usage_mb: float
    uptime_seconds: float
    version: str
