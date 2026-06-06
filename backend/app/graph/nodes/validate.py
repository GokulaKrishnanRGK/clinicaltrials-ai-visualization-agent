from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.graph.nodes._helpers import build_meta
from app.graph.state import GraphState
from app.schemas.responses import VisualizationApiResponse, VisualizationMessageResponse
from app.services.cache.fixtures import get_cache_fixture_data_source

_ResponseAdapter = TypeAdapter(VisualizationApiResponse)


def validate_response(state: GraphState) -> dict[str, Any]:
    raw = state.get("final_response")
    if not raw:
        meta = build_meta(state, records_retrieved=0, records_used=0)
        msg = VisualizationMessageResponse(
            request_id=state["request_id"],
            message="No response was generated.",
            reason="validation_failure",
            meta=meta,
        )
        return {"final_response": msg.model_dump(mode="json")}
    try:
        _ResponseAdapter.validate_python(raw)
    except ValidationError:
        meta = build_meta(state, records_retrieved=0, records_used=0)
        msg = VisualizationMessageResponse(
            request_id=state["request_id"],
            message="Generated response failed schema validation.",
            reason="validation_failure",
            meta=meta,
        )
        return {"final_response": msg.model_dump(mode="json")}
    return {}


def message_insufficient(state: GraphState) -> dict[str, Any]:
    meta = build_meta(
        state,
        records_retrieved=state.get("records_retrieved", 0),
        records_used=0,
    )
    ds = get_cache_fixture_data_source()
    suggested = [f["query"] for f in ds._manifest.get("fixtures", [])[:3]]
    msg = VisualizationMessageResponse(
        request_id=state["request_id"],
        message=(
            "Not enough trial records were retrieved to build a visualization. "
            "Try a more specific condition, drug, or sponsor."
        ),
        reason="insufficient_data",
        suggested_queries=suggested,
        meta=meta,
    )
    return {"final_response": msg.model_dump(mode="json")}
