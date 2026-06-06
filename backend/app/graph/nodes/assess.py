from __future__ import annotations

from typing import Any

from app.graph.state import GraphState


def assess_data_sufficiency(state: GraphState) -> dict[str, Any]:
    return {}


def repair_plan(state: GraphState) -> dict[str, Any]:
    params = dict(state.get("retrieval_params") or {})
    repair_count = state.get("repair_count", 0)

    removed = False
    for key in ("trial_phase", "status", "country"):
        if key in params:
            params.pop(key)
            removed = True
            break
    if not removed:
        params["max_records"] = min(params.get("max_records", state["max_records"]) * 2, 1000)

    return {"retrieval_params": params, "repair_count": repair_count + 1}
