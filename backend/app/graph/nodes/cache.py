from __future__ import annotations

from typing import Any

from app.graph.state import GraphState
from app.services.cache.fixtures import CacheFixtureNotFoundError, get_cache_fixture_data_source

_FIXTURE_KEYWORDS: dict[str, list[str]] = {
    "pembrolizumab_trials_by_year": ["pembrolizumab", "year"],
    "alzheimers_recruiting_by_country": ["alzheimer", "country"],
    "oncology_phase_status": ["oncology", "phase", "status"],
    "phase3_breast_cancer_sponsors": ["breast", "cancer", "sponsor"],
    "diabetes_drug_sponsor_network": ["diabetes", "network"],
    "phase3_sites_by_country": ["phase", "3", "site", "country"],
}


def _score_fixture(query: str, fixture_id: str) -> int:
    query_lower = query.lower()
    return sum(1 for kw in _FIXTURE_KEYWORDS.get(fixture_id, []) if kw in query_lower)


def _apply_citation_limit(response: dict[str, Any], limit: int) -> dict[str, Any]:
    if response.get("status") != "visualization":
        return response
    viz = response.get("visualization", {})
    data = viz.get("data")
    if isinstance(data, list):
        for datum in data:
            if isinstance(datum, dict) and "citations" in datum:
                datum["citations"] = datum["citations"][:limit]
    elif isinstance(data, dict):
        for node in data.get("nodes", []):
            if isinstance(node, dict) and "citations" in node:
                node["citations"] = node["citations"][:limit]
        for edge in data.get("edges", []):
            if isinstance(edge, dict) and "citations" in edge:
                edge["citations"] = edge["citations"][:limit]
    return response


def cache_lookup(state: GraphState) -> dict[str, Any]:
    ds = get_cache_fixture_data_source()
    identifiers = ds.list_identifiers()
    query = state["query"]

    best_id = max(identifiers, key=lambda fid: _score_fixture(query, fid), default=None)
    score = _score_fixture(query, best_id) if best_id else 0

    if best_id and score >= 1:
        try:
            fixture_response = ds.get_response(best_id)
            serialized = fixture_response.model_dump(mode="json")
            serialized["request_id"] = state["request_id"]
            serialized = _apply_citation_limit(serialized, state["citation_limit"])
            return {"final_response": serialized}
        except (CacheFixtureNotFoundError, Exception):
            pass

    miss = ds.cache_miss_response(state["request_id"], query)
    return {"final_response": miss.model_dump(mode="json")}
