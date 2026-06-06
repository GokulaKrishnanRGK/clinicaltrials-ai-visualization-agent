from __future__ import annotations

from typing import Any

from app.graph.nodes._helpers import build_meta, intent_from_state
from app.graph.state import GraphState
from app.logging_config import get_logger
from app.schemas.responses import VisualizationMessageResponse

logger = get_logger(__name__)

_OUT_OF_SCOPE_MESSAGE = (
    "This application only answers questions about clinical trials — "
    "drugs, conditions, trial phases, sponsors, enrollment, and related topics. "
    "Please rephrase your question around clinical trial data."
)

_SUGGESTED_QUERIES = [
    "Show trials for semaglutide by phase",
    "How many Alzheimer's trials are active in the US?",
    "Top sponsors for oncology trials",
]


async def interpret_question(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    logger.debug("interpret_question start request_id=%s query=%r", rid, state["query"][:120])
    try:
        from pydantic import BaseModel, Field

        from app.services.llm.client import LLMClient

        class ParsedQuery(BaseModel):
            in_scope: bool = True
            drug_name: str | None = None
            condition: str | None = None
            trial_phase: str | None = None
            sponsor: str | None = None
            country: str | None = None
            status: str | None = None
            start_year: int | None = None
            end_year: int | None = None
            preferred_visualization: str | None = None
            assumptions: list[str] = Field(default_factory=list)
            warnings: list[str] = Field(default_factory=list)

        client = LLMClient()
        parsed = await client.complete_structured(
            prompt_id="query_parser",
            response_model=ParsedQuery,
            variables={"query": state["query"], "request": intent_from_state(state)},
        )

        if not parsed.in_scope:
            logger.info("interpret_question out_of_scope request_id=%s query=%r", rid, state["query"][:120])
            meta = build_meta(state, records_retrieved=0, records_used=0)
            msg = VisualizationMessageResponse(
                request_id=state["request_id"],
                message=_OUT_OF_SCOPE_MESSAGE,
                reason="unsupported_query",
                suggested_queries=_SUGGESTED_QUERIES,
                meta=meta,
            )
            return {"final_response": msg.model_dump(mode="json")}

        interpreted = parsed.model_dump(exclude={"in_scope", "assumptions", "warnings"})
        active_filters = {k: v for k, v in interpreted.items() if v is not None}
        logger.info(
            "interpret_question complete request_id=%s filters=%s assumptions=%d warnings=%d",
            rid,
            active_filters,
            len(parsed.assumptions),
            len(parsed.warnings),
        )
        return {
            "interpreted": interpreted,
            "assumptions": parsed.assumptions,
            "warnings": parsed.warnings,
        }
    except Exception:
        logger.warning("interpret_question failed request_id=%s — falling back to raw state", rid, exc_info=True)
        return {
            "interpreted": intent_from_state(state),
            "assumptions": [],
            "warnings": [],
        }


def create_retrieval_plan(state: GraphState) -> dict[str, Any]:
    intent = state.get("interpreted") or intent_from_state(state)
    params: dict[str, Any] = {
        "query": state["query"],
        "max_records": state["max_records"],
    }
    for key in ("drug_name", "condition", "trial_phase", "sponsor", "country", "status"):
        if intent.get(key):
            params[key] = intent[key]
    for key in ("start_year", "end_year"):
        if intent.get(key) is not None:
            params[key] = intent[key]
    return {"retrieval_params": params}
