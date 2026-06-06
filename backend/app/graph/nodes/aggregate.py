from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.clinical_trials import NormalizedTrialRecord
from app.services import aggregation as agg

logger = get_logger(__name__)
_RecordAdapter = TypeAdapter(list[NormalizedTrialRecord])


def _choose_agg_type(state: GraphState) -> str:
    query = state["query"].lower()
    interpreted = state.get("interpreted") or {}
    pref = (
        interpreted.get("preferred_visualization") or state.get("preferred_visualization") or ""
    ).lower()

    if "network" in pref or any(kw in query for kw in ("network", "graph", "map")):
        return "drug_sponsor_network"

    if any(kw in query for kw in ("year", "since", "trend", "over time", "timeline")):
        return "by_year"

    if any(kw in query for kw in ("country", "countries", "location", "site", "region")):
        return "by_country"

    if any(kw in query for kw in ("sponsor", "company", "manufacturer", "funder")):
        return "by_sponsor"

    if "phase" in query and any(kw in query for kw in ("status", "recruiting", "active")):
        return "by_phase_and_status"

    if "phase" in query:
        return "by_phase"

    if any(kw in query for kw in ("status", "recruiting", "completed")):
        return "by_status"

    return "by_phase"


def aggregate_data(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    records = _RecordAdapter.validate_python(state.get("records", []))
    agg_type = _choose_agg_type(state)
    limit = state["citation_limit"]
    logger.debug(
        "aggregate_data request_id=%s agg_type=%s record_count=%d citation_limit=%d",
        rid, agg_type, len(records), limit,
    )

    if agg_type == "by_year":
        from_year = state.get("start_year") or (state.get("interpreted") or {}).get("start_year")
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
    elif agg_type == "drug_cooccurrence_network":
        data = agg.build_drug_cooccurrence_network(records, citation_limit=limit)
    else:
        data = agg.build_drug_sponsor_network(records, citation_limit=limit)

    logger.info("aggregate_data complete request_id=%s agg_type=%s rows=%d", rid, agg_type, len(data) if isinstance(data, list) else 1)
    return {"agg_type": agg_type, "agg_data": data}
