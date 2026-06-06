from __future__ import annotations

from typing import Any

from app.graph.nodes._helpers import build_meta
from app.graph.state import GraphState
from app.schemas.responses import VisualizationMessageResponse
from app.services.clinical_trials.invoker import ClinicalTrialsToolError, ClinicalTrialsToolInvoker


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

    params = state.get("retrieval_params") or {}
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
            data_mode="live",
        )
    except Exception as exc:
        return _api_failure_response(state, str(exc))

    invoker = ClinicalTrialsToolInvoker()
    try:
        result = await invoker.invoke(request)
    except ClinicalTrialsToolError as exc:
        return _api_failure_response(state, str(exc))

    return {
        "records": [r.model_dump(mode="json") for r in result.records],
        "records_retrieved": result.records_retrieved,
        "tool_warnings": result.warnings,
    }
