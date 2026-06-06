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


def _build_request(params: dict, state: GraphState, drug_name: str | None, max_records: int):
    from app.schemas.requests import VisualizationRequest

    return VisualizationRequest(
        query=params.get("query", state["query"]),
        drug_name=drug_name,
        condition=params.get("condition"),
        sponsor=params.get("sponsor"),
        country=params.get("country"),
        status=params.get("status"),
        start_year=params.get("start_year"),
        end_year=params.get("end_year"),
        max_records=max_records,
    )


async def execute_tools(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    params = state.get("retrieval_params") or {}
    logger.debug("execute_tools start request_id=%s params=%s", rid, params)

    drug_name_2 = params.get("drug_name_2")

    if drug_name_2 and params.get("drug_name"):
        return await _execute_comparison(state, params, rid)

    try:
        max_rec = params.get("max_records", state["max_records"])
        request = _build_request(params, state, params.get("drug_name"), max_rec)
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
    if logger.isEnabledFor(10) and result.records:
        preview = [
            {
                "nct_id": d.get("nct_id"),
                "title": (d.get("brief_title") or "")[:60],
                "status": d.get("overall_status"),
            }
            for d in (r.model_dump(mode="json") for r in result.records[:3])
        ]
        logger.debug(
            "execute_tools records_preview request_id=%s total=%d preview=%s",
            rid,
            len(result.records),
            preview,
        )
    return {
        "records": [r.model_dump(mode="json") for r in result.records],
        "records_retrieved": result.records_retrieved,
        "tool_warnings": result.warnings,
    }


async def _execute_comparison(
    state: GraphState, params: dict, rid: str
) -> dict[str, Any]:
    """Fetch records for two drugs sequentially and tag each with comparison_drug."""
    drug_names = [params["drug_name"], params["drug_name_2"]]
    per_drug_max = max(1, params.get("max_records", state["max_records"]) // 2)
    invoker = ClinicalTrialsToolInvoker()

    all_records: list[dict] = []
    total_retrieved = 0
    all_warnings: list[str] = []

    for drug in drug_names:
        try:
            request = _build_request(params, state, drug, per_drug_max)
        except Exception as exc:
            logger.warning(
                "execute_tools comparison invalid_params request_id=%s drug=%r error=%s",
                rid, drug, exc,
            )
            continue
        try:
            result = await invoker.invoke(request)
        except ClinicalTrialsToolError as exc:
            logger.warning(
                "execute_tools comparison api_failure request_id=%s drug=%r error=%s",
                rid, drug, exc,
            )
            continue

        tagged = [
            dict(r.model_dump(mode="json"), comparison_drug=drug)
            for r in result.records
        ]
        all_records.extend(tagged)
        total_retrieved += result.records_retrieved
        all_warnings.extend(result.warnings)
        logger.info(
            "execute_tools comparison_fetch request_id=%s drug=%r "
            "retrieved=%d normalized=%d",
            rid, drug, result.records_retrieved, len(result.records),
        )

    logger.info(
        "execute_tools complete request_id=%s mode=comparison "
        "records_retrieved=%d records_normalized=%d",
        rid, total_retrieved, len(all_records),
    )
    return {
        "records": all_records,
        "records_retrieved": total_retrieved,
        "tool_warnings": all_warnings,
    }
