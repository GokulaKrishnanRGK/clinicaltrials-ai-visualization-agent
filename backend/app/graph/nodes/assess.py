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
            "assess_data_sufficiency sufficient request_id=%s record_count=%d",
            rid,
            record_count,
        )
    else:
        logger.info(
            "assess_data_sufficiency insufficient request_id=%s "
            "record_count=%d min=%d repair_count=%d",
            rid,
            record_count,
            _MIN_RECORDS,
            repair_count,
        )

    return {"records_sufficient": sufficient}


def repair_plan(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    params = dict(state.get("retrieval_params") or {})
    repair_count = state.get("repair_count", 0)

    removed = False
    for key in ("trial_phase", "status", "country"):
        if key in params:
            params.pop(key)
            removed = True
            logger.info(
                "repair_plan request_id=%s attempt=%d dropped_filter=%s",
                rid,
                repair_count + 1,
                key,
            )
            break
    if not removed:
        new_max = min(params.get("max_records", state["max_records"]) * 2, 1000)
        params["max_records"] = new_max
        logger.info(
            "repair_plan request_id=%s attempt=%d expanded_max_records=%d",
            rid,
            repair_count + 1,
            new_max,
        )

    return {"retrieval_params": params, "repair_count": repair_count + 1}
