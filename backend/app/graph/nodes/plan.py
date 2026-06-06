from __future__ import annotations

import json
from typing import Any

from app.graph.nodes._helpers import intent_from_state
from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.plan import AGG_TYPES, FetchSpec, RetrievalPlan

logger = get_logger(__name__)


def _fallback_plan(state: GraphState) -> dict[str, Any]:
    """Single-call plan built from interpreted state when the LLM plan fails."""
    intent = state.get("interpreted") or intent_from_state(state)
    spec: dict[str, Any] = {
        "label": intent.get("drug_name") or intent.get("condition") or "Results",
        "max_records": state["max_records"],
    }
    for key in ("drug_name", "condition", "country", "status", "trial_phase", "sponsor",
                "start_year", "end_year"):
        if intent.get(key):
            spec[key] = intent[key]

    has_years = bool(intent.get("start_year") and intent.get("end_year"))
    agg_type = "by_year" if has_years else "by_phase"
    return RetrievalPlan(calls=[FetchSpec(**spec)], agg_type=agg_type).model_dump()


async def plan_tool_calls(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    intent = state.get("interpreted") or intent_from_state(state)
    active_intent = {k: v for k, v in intent.items() if v is not None}
    logger.debug(
        "plan_tool_calls input request_id=%s intent=%s max_records=%d",
        rid, active_intent, state["max_records"],
    )

    try:
        from app.services.llm.client import LLMClient

        client = LLMClient()
        plan: RetrievalPlan = await client.complete_structured(
            prompt_id="tool_planner",
            response_model=RetrievalPlan,
            variables={
                "query": state["query"],
                "intent": json.dumps(active_intent),
                "max_records": state["max_records"],
            },
        )

        if plan.agg_type not in AGG_TYPES:
            logger.warning(
                "plan_tool_calls unknown_agg_type request_id=%s agg_type=%r — using by_phase",
                rid, plan.agg_type,
            )
            plan = RetrievalPlan(calls=plan.calls, agg_type="by_phase")

    except Exception as exc:
        logger.warning(
            "plan_tool_calls failed request_id=%s error=%s — using fallback plan",
            rid, exc, exc_info=True,
        )
        return {"retrieval_plan": _fallback_plan(state), "node_summary": "Plan failed — single-call fallback"}

    plan_dict = plan.model_dump()
    logger.info(
        "plan_tool_calls complete request_id=%s calls=%d agg_type=%s labels=%s",
        rid,
        len(plan.calls),
        plan.agg_type,
        [c.label for c in plan.calls],
    )
    logger.debug("plan_tool_calls output request_id=%s plan=%s", rid, plan_dict)
    labels = [c.label for c in plan.calls]
    node_summary = f"{len(labels)} call(s): {', '.join(labels[:3])} · agg: {plan.agg_type}"
    return {"retrieval_plan": plan_dict, "node_summary": node_summary}
