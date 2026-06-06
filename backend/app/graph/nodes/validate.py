from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.graph.nodes._helpers import build_meta
from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.responses import VisualizationApiResponse, VisualizationMessageResponse

logger = get_logger(__name__)
_ResponseAdapter = TypeAdapter(VisualizationApiResponse)

_SUGGESTED_QUERIES = [
    "Show trials for semaglutide by phase",
    "How many Alzheimer's trials are active in the US?",
    "Top sponsors for oncology trials",
]


def validate_response(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    raw = state.get("final_response")
    logger.debug(
        "validate_response input request_id=%s status=%s",
        rid,
        raw.get("status") if isinstance(raw, dict) else None,
    )
    if not raw:
        logger.warning("validate_response no response generated request_id=%s", rid)
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
    except ValidationError as exc:
        logger.warning("validate_response schema_failure request_id=%s error=%s", rid, exc)
        meta = build_meta(state, records_retrieved=0, records_used=0)
        msg = VisualizationMessageResponse(
            request_id=state["request_id"],
            message="Generated response failed schema validation.",
            reason="validation_failure",
            meta=meta,
        )
        return {"final_response": msg.model_dump(mode="json")}
    viz_type = (
        raw.get("visualization", {}).get("type")
        if isinstance(raw, dict)
        else None
    )
    logger.debug("validate_response ok request_id=%s viz_type=%s", rid, viz_type)
    return {}


def message_insufficient(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    logger.info(
        "message_insufficient request_id=%s records_retrieved=%d",
        rid, state.get("records_retrieved", 0),
    )
    meta = build_meta(
        state,
        records_retrieved=state.get("records_retrieved", 0),
        records_used=0,
    )
    msg = VisualizationMessageResponse(
        request_id=state["request_id"],
        message=(
            "Not enough trial records were retrieved to build a visualization. "
            "Try a more specific condition, drug, or sponsor."
        ),
        reason="insufficient_data",
        suggested_queries=_SUGGESTED_QUERIES,
        meta=meta,
    )
    logger.debug(
        "message_insufficient output request_id=%s reason=%s message=%r",
        rid,
        msg.reason,
        msg.message[:80],
    )
    records_retrieved = state.get("records_retrieved", 0)
    return {
        "final_response": msg.model_dump(mode="json"),
        "node_summary": f"Insufficient data · {records_retrieved} records retrieved",
    }
