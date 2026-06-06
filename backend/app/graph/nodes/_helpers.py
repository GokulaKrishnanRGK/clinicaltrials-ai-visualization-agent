from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.graph.state import GraphState
from app.schemas.responses import ResponseMetadata


def build_meta(state: GraphState, *, records_retrieved: int, records_used: int) -> ResponseMetadata:
    filters: dict[str, Any] = {"query": state["query"]}
    for key in ("drug_name", "condition", "trial_phase", "sponsor", "country", "status"):
        val = state.get(key)
        if val:
            filters[key] = val
    for key in ("start_year", "end_year"):
        val = state.get(key)
        if val is not None:
            filters[key] = val
    return ResponseMetadata(
        filters=filters,
        records_retrieved=records_retrieved,
        records_used=records_used,
        generated_at=datetime.now(UTC),
    )


def intent_from_state(state: GraphState) -> dict[str, Any]:
    return {
        "drug_name": state.get("drug_name"),
        "condition": state.get("condition"),
        "trial_phase": state.get("trial_phase"),
        "sponsor": state.get("sponsor"),
        "country": state.get("country"),
        "status": state.get("status"),
        "start_year": state.get("start_year"),
        "end_year": state.get("end_year"),
        "preferred_visualization": state.get("preferred_visualization"),
    }
