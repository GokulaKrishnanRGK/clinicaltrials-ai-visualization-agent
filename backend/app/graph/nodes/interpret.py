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
        from pydantic import BaseModel, ConfigDict, Field, model_validator

        from app.services.llm.client import LLMClient

        class ParsedQuery(BaseModel):
            model_config = ConfigDict(extra="ignore")

            in_scope: bool = True
            drug_name: str | None = None
            drug_name_2: str | None = None
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

            @model_validator(mode="before")
            @classmethod
            def _coerce_null_lists(cls, data: object) -> object:
                if isinstance(data, dict):
                    for key in ("assumptions", "warnings"):
                        if data.get(key) is None:
                            data[key] = []
                return data

        client = LLMClient()
        parsed = await client.complete_structured(
            prompt_id="query_parser",
            response_model=ParsedQuery,
            variables={"query": state["query"], "request": intent_from_state(state)},
        )

        logger.debug(
            "interpret_question parsed request_id=%s fields=%s",
            rid,
            parsed.model_dump(exclude={"assumptions", "warnings"}),
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
    except Exception as exc:
        logger.warning(
            "interpret_question failed request_id=%s error=%s — falling back to raw state",
            rid,
            exc,
            exc_info=True,
        )
        fallback = intent_from_state(state)
        active = {k: v for k, v in fallback.items() if v is not None}
        logger.info("interpret_question fallback request_id=%s fields=%s", rid, active)
        return {
            "interpreted": fallback,
            "assumptions": [],
            "warnings": [],
        }


