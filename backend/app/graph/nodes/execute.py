from __future__ import annotations

from typing import Any

from app.graph.nodes._helpers import build_meta
from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.responses import VisualizationMessageResponse
from app.services.clinical_trials.invoker import ClinicalTrialsToolError, ClinicalTrialsToolInvoker

logger = get_logger(__name__)


def _api_failure_response(state: GraphState, detail: str) -> dict[str, Any]:
    meta = build_meta(state, records_retrieved=0, records_used=0)
    msg = VisualizationMessageResponse(
        request_id=state["request_id"],
        message=f"ClinicalTrials.gov API call failed: {detail}",
        reason="api_failure",
        meta=meta,
    )
    return {"final_response": msg.model_dump(mode="json"), "records": [], "records_retrieved": 0}


async def execute_tools(state: GraphState) -> dict[str, Any]:
    from app.schemas.requests import VisualizationRequest

    rid = state["request_id"]
    params = state.get("retrieval_params") or {}
    logger.debug("execute_tools start request_id=%s params=%s", rid, params)

    try:
        request = VisualizationRequest(
            query=params.get("query", state["query"]),
            drug_name=params.get("drug_name"),
            condition=params.get("condition"),
            sponsor=params.get("sponsor"),
            country=params.get("country"),
            status=params.get("status"),
            start_year=params.get("start_year"),
            end_year=params.get("end_year"),
            max_records=params.get("max_records", state["max_records"]),
        )
    except Exception as exc:
        logger.warning("execute_tools invalid params request_id=%s error=%s", rid, exc)
        return _api_failure_response(state, str(exc))

    invoker = ClinicalTrialsToolInvoker()
    try:
        result = await invoker.invoke(request)
    except ClinicalTrialsToolError as exc:
        logger.warning("execute_tools api_failure request_id=%s error=%s", rid, exc)
        return _api_failure_response(state, str(exc))

    logger.info(
        "execute_tools complete request_id=%s records_retrieved=%d records_normalized=%d warnings=%d",
        rid,
        result.records_retrieved,
        len(result.records),
        len(result.warnings),
    )
    return {
        "records": [r.model_dump(mode="json") for r in result.records],
        "records_retrieved": result.records_retrieved,
        "tool_warnings": result.warnings,
    }
