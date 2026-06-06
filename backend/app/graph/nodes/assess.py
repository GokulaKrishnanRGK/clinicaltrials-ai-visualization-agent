from __future__ import annotations

from typing import Any

from app.graph.state import GraphState
from app.logging_config import get_logger

logger = get_logger(__name__)

# Minimum number of records needed to produce a meaningful visualization.
_MIN_RECORDS = 3


def assess_data_sufficiency(state: GraphState) -> dict[str, Any]:
    """Decide whether the retrieved records are sufficient to visualize.

    Writes `records_sufficient` into state. The routing edge reads that field
    to decide whether to aggregate, repair, or give up.
    """
    rid = state["request_id"]
    records = state.get("records", [])
    record_count = len(records)
    repair_count = state.get("repair_count", 0)

    sufficient = record_count >= _MIN_RECORDS

    if sufficient:
        logger.debug(
            "assess_data_sufficiency output request_id=%s "
            "record_count=%d records_sufficient=True",
            rid,
            record_count,
        )
    else:
        logger.info(
            "assess_data_sufficiency output request_id=%s "
            "record_count=%d min=%d repair_count=%d records_sufficient=False",
            rid,
            record_count,
            _MIN_RECORDS,
            repair_count,
        )

    if sufficient:
        node_summary = f"Sufficient — {record_count} records"
    else:
        node_summary = f"Insufficient — {record_count} records (need ≥ {_MIN_RECORDS})"
    return {"records_sufficient": sufficient, "node_summary": node_summary}


def repair_plan(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    repair_count = state.get("repair_count", 0)
    plan = dict(state.get("retrieval_plan") or {})
    calls = [dict(c) for c in plan.get("calls") or []]

    logger.debug(
        "repair_plan input request_id=%s attempt=%d calls=%d",
        rid, repair_count + 1, len(calls),
    )

    for call in calls:
        old = call.get("max_records", 200)
        call["max_records"] = min(old * 2, 500)

    new_max = calls[0]["max_records"] if calls else 200
    logger.info(
        "repair_plan request_id=%s attempt=%d expanded_max_records_per_call=%d",
        rid, repair_count + 1, new_max,
    )

    plan["calls"] = calls
    logger.debug("repair_plan output request_id=%s plan=%s", rid, plan)
    return {
        "retrieval_plan": plan,
        "repair_count": repair_count + 1,
        "node_summary": f"Repair #{repair_count + 1} — expanded max to {new_max}",
    }
