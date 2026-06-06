from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.clinical_trials import NormalizedTrialRecord
from app.services import aggregation as agg

logger = get_logger(__name__)
_RecordAdapter = TypeAdapter(list[NormalizedTrialRecord])


def aggregate_data(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    plan = state.get("retrieval_plan") or {}
    agg_type = plan.get("agg_type") or "by_phase"
    limit = state["citation_limit"]
    raw_records = state.get("records", [])

    logger.debug(
        "aggregate_data input request_id=%s agg_type=%s record_count=%d citation_limit=%d",
        rid, agg_type, len(raw_records), limit,
    )

    if agg_type == "by_phase_per_label":
        # Records are tagged dicts with a `label` field — skip NormalizedTrialRecord validation.
        data = agg.count_by_phase_per_label(raw_records, citation_limit=limit)
    else:
        records = _RecordAdapter.validate_python(raw_records)
        if agg_type == "by_year":
            from_year = (state.get("interpreted") or {}).get("start_year")
            data = agg.count_by_year(records, from_year=from_year, citation_limit=limit)
        elif agg_type == "by_country":
            data = agg.count_by_country(records, citation_limit=limit)
        elif agg_type == "by_phase":
            data = agg.count_by_phase(records, citation_limit=limit)
        elif agg_type == "by_status":
            data = agg.count_by_status(records, citation_limit=limit)
        elif agg_type == "by_phase_and_status":
            data = agg.count_by_phase_and_status(records, citation_limit=limit)
        elif agg_type == "by_sponsor":
            data = agg.count_by_sponsor(records, citation_limit=limit)
        elif agg_type == "scatter_by_year":
            data = agg.scatter_interventions_by_year(records, citation_limit=limit)
        elif agg_type == "histogram_by_year":
            data = agg.histogram_start_years(records, citation_limit=limit)
        elif agg_type == "drug_cooccurrence_network":
            data = agg.build_drug_cooccurrence_network(records, citation_limit=limit)
        elif agg_type == "drug_condition_network":
            data = agg.build_drug_condition_network(records, citation_limit=limit)
        else:
            data = agg.build_drug_sponsor_network(records, citation_limit=limit)

    row_count = len(data) if isinstance(data, list) else 1
    logger.info(
        "aggregate_data output request_id=%s agg_type=%s rows=%d", rid, agg_type, row_count
    )
    if logger.isEnabledFor(10) and isinstance(data, list) and data:
        first = {k: v for k, v in data[0].items() if k != "citations"}
        logger.debug("aggregate_data first_row request_id=%s row=%s", rid, first)
    return {"agg_type": agg_type, "agg_data": data, "node_summary": f"{row_count} point(s) · method: {agg_type}"}
