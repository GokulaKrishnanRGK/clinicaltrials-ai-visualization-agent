from __future__ import annotations

from typing import Any

from app.graph.state import GraphState
from app.logging_config import get_logger

logger = get_logger(__name__)


def assess_data_sufficiency(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    record_count = len(state.get("records", []))
    logger.debug(
        "assess_data_sufficiency request_id=%s record_count=%d repair_count=%d",
        rid, record_count, state.get("repair_count", 0),
    )
    return {}


def repair_plan(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    params = dict(state.get("retrieval_params") or {})
    repair_count = state.get("repair_count", 0)

    removed = False
    for key in ("trial_phase", "status", "country"):
        if key in params:
            params.pop(key)
            removed = True
            logger.info("repair_plan request_id=%s attempt=%d dropped_filter=%s", rid, repair_count + 1, key)
            break
    if not removed:
        new_max = min(params.get("max_records", state["max_records"]) * 2, 1000)
        params["max_records"] = new_max
        logger.info("repair_plan request_id=%s attempt=%d expanded_max_records=%d", rid, repair_count + 1, new_max)

    return {"retrieval_params": params, "repair_count": repair_count + 1}
