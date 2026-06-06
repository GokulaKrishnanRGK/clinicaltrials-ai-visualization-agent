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


async def execute_tool_calls(state: GraphState) -> dict[str, Any]:
    from app.schemas.requests import VisualizationRequest

    rid = state["request_id"]
    plan = state.get("retrieval_plan") or {}
    calls = plan.get("calls") or []

    if not calls:
        logger.warning("execute_tool_calls no_calls request_id=%s — no calls in plan", rid)
        return {**_api_failure_response(state, "retrieval plan produced no API calls"), "node_summary": "No calls in plan — API failure"}

    logger.debug(
        "execute_tool_calls start request_id=%s calls=%d agg_type=%s",
        rid, len(calls), plan.get("agg_type"),
    )

    invoker = ClinicalTrialsToolInvoker()
    all_records: list[dict[str, Any]] = []
    total_retrieved = 0
    all_warnings: list[str] = []

    for spec in calls:
        label = spec.get("label", "Results")
        try:
            request = VisualizationRequest(
                query=state["query"],
                drug_name=spec.get("drug_name"),
                condition=spec.get("condition"),
                sponsor=spec.get("sponsor"),
                country=spec.get("country"),
                status=spec.get("status"),
                start_year=spec.get("start_year"),
                end_year=spec.get("end_year"),
                max_records=spec.get("max_records", state["max_records"]),
            )
        except Exception as exc:
            logger.warning(
                "execute_tool_calls invalid_spec request_id=%s label=%r error=%s",
                rid, label, exc,
            )
            continue

        try:
            result = await invoker.invoke(request)
        except ClinicalTrialsToolError as exc:
            logger.warning(
                "execute_tool_calls api_failure request_id=%s label=%r error=%s",
                rid, label, exc,
            )
            continue

        tagged = [
            dict(r.model_dump(mode="json"), label=label)
            for r in result.records
        ]
        all_records.extend(tagged)
        total_retrieved += result.records_retrieved
        all_warnings.extend(result.warnings)
        logger.info(
            "execute_tool_calls fetch_complete request_id=%s label=%r "
            "retrieved=%d normalized=%d",
            rid, label, result.records_retrieved, len(result.records),
        )

    if not all_records and not total_retrieved:
        return {**_api_failure_response(state, "all API calls failed or returned no data"), "node_summary": "All API calls failed"}

    logger.info(
        "execute_tool_calls complete request_id=%s total_retrieved=%d total_normalized=%d",
        rid, total_retrieved, len(all_records),
    )
    if logger.isEnabledFor(10) and all_records:
        preview = [
            {
                "nct_id": r.get("nct_id"),
                "label": r.get("label"),
                "title": (r.get("brief_title") or "")[:60],
            }
            for r in all_records[:3]
        ]
        logger.debug(
            "execute_tool_calls records_preview request_id=%s total=%d preview=%s",
            rid, len(all_records), preview,
        )

    return {
        "records": all_records,
        "records_retrieved": total_retrieved,
        "tool_warnings": all_warnings,
        "node_summary": f"{total_retrieved} records fetched · {len(calls)} call(s)",
    }


# keep old name as alias so any direct import still works during transition
execute_tools = execute_tool_calls
