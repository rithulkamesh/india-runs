import sys
from collections import Counter
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from api.models.schemas import (
    CompanyNode,
    GraphData,
    RelatedCandidate,
    SkillNode,
)

sys.path.insert(0, ".")

from src.data.skill_ontology import SKILL_GROUPS, get_skill_group, get_skill_weight

router = APIRouter(prefix="/api/graph")

_SHARED_SKILL_THRESHOLD = 3
_SHARED_COMPANY_THRESHOLD = 1


@router.get("/{candidate_id}", response_model=GraphData)
def get_graph(request: Request, candidate_id: str) -> GraphData:
    index = request.app.state.id_index
    candidate = index.get(candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    skill_nodes = _build_skill_nodes(candidate)
    skill_edges = _build_skill_edges(skill_nodes)

    company_nodes = _build_company_nodes(candidate)
    company_edges = _build_company_edges(company_nodes)

    related = _find_related(candidate_id, candidate, index)

    return GraphData(
        candidate_id=candidate_id,
        skill_nodes=skill_nodes,
        skill_edges=skill_edges,
        company_nodes=company_nodes,
        company_edges=company_edges,
        related_candidates=related,
    )


def _build_skill_nodes(candidate: dict) -> list[SkillNode]:
    nodes: list[SkillNode] = []
    seen: set[str] = set()
    for s in candidate.get("skills", []):
        name = s["name"]
        if name in seen:
            continue
        seen.add(name)
        group = get_skill_group(name)
        weight = get_skill_weight(name)
        if weight > 0:
            nodes.append(SkillNode(
                name=name,
                group=group,
                weight=weight,
                endorsements=s.get("endorsements", 0),
                proficiency=s.get("proficiency"),
            ))
    nodes.sort(key=lambda n: n.weight, reverse=True)
    return nodes[:30]


def _build_skill_edges(nodes: list[SkillNode]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    group_members: dict[str, list[str]] = {}
    for n in nodes:
        if n.group:
            group_members.setdefault(n.group, []).append(n.name)

    for group, members in group_members.items():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                edges.append({
                    "source": members[i],
                    "target": members[j],
                    "type": "co_group",
                    "group": group,
                })
    return edges


def _build_company_nodes(candidate: dict) -> list[CompanyNode]:
    nodes: list[CompanyNode] = []
    seen: set[str] = set()
    current_company = candidate.get("profile", {}).get("current_company", "").lower()
    for role in candidate.get("career_history", []):
        company = role.get("company", "")
        company_lower = company.lower()
        if not company or company_lower in seen:
            continue
        seen.add(company_lower)
        nodes.append(CompanyNode(
            name=company,
            role_count=1,
            is_current=(company_lower == current_company),
        ))
    nodes.sort(key=lambda n: (not n.is_current, n.name))
    return nodes


def _build_company_edges(nodes: list[CompanyNode]) -> list[dict[str, Any]]:
    if len(nodes) < 2:
        return []
    edges: list[dict[str, Any]] = []
    for i in range(len(nodes) - 1):
        edges.append({
            "source": nodes[i].name,
            "target": nodes[i + 1].name,
            "type": "career_progression",
        })
    return edges


def _find_related(
    candidate_id: str,
    candidate: dict,
    index: dict[str, dict],
) -> list[RelatedCandidate]:
    candidate_skills = {s["name"].lower() for s in candidate.get("skills", [])}
    candidate_companies = set()
    for role in candidate.get("career_history", []):
        if role.get("company"):
            candidate_companies.add(role["company"].lower())

    related: list[RelatedCandidate] = []
    for other_id, other in index.items():
        if other_id == candidate_id:
            continue

        other_skills = {s["name"].lower() for s in other.get("skills", [])}
        shared_skills = list(candidate_skills & other_skills)
        if len(shared_skills) < _SHARED_SKILL_THRESHOLD:
            continue

        other_companies = set()
        for role in other.get("career_history", []):
            if role.get("company"):
                other_companies.add(role["company"].lower())
        shared_companies = [c for c in candidate_companies & other_companies]

        similarity = len(shared_skills) / max(len(candidate_skills), 1)
        other_profile = other.get("profile", {})

        related.append(RelatedCandidate(
            candidate_id=other_id,
            name=other_profile.get("full_name", ""),
            title=other_profile.get("current_title", ""),
            shared_skills=shared_skills[:10],
            shared_companies=shared_companies[:5],
            similarity=round(similarity, 3),
        ))

    related.sort(key=lambda r: r.similarity, reverse=True)
    return related[:20]
