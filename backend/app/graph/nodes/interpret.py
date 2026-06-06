from __future__ import annotations

from typing import Any

from app.graph.nodes._helpers import intent_from_state
from app.graph.state import GraphState


async def interpret_question(state: GraphState) -> dict[str, Any]:
    try:
        from pydantic import BaseModel, Field

        from app.services.llm.client import LLMClient

        class ParsedQuery(BaseModel):
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
        return {
            "interpreted": parsed.model_dump(exclude={"assumptions", "warnings"}),
            "assumptions": parsed.assumptions,
            "warnings": parsed.warnings,
        }
    except Exception:
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
        "data_mode": state["data_mode"],
    }
    for key in ("drug_name", "condition", "trial_phase", "sponsor", "country", "status"):
        if intent.get(key):
            params[key] = intent[key]
    for key in ("start_year", "end_year"):
        if intent.get(key) is not None:
            params[key] = intent[key]
    return {"retrieval_params": params}
