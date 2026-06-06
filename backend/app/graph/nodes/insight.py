from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from app.graph.state import GraphState
from app.logging_config import get_logger

logger = get_logger(__name__)


class _InsightResponse(BaseModel):
    insight: str = ""


def _top_data(visualization: dict[str, Any]) -> list[dict[str, Any]]:
    """Return up to 5 representative data points stripped of citation arrays."""
    viz_type = visualization.get("type", "")
    data = visualization.get("data", [])
    encoding = visualization.get("encoding", {})

    if viz_type == "network_graph":
        nodes = data.get("nodes", []) if isinstance(data, dict) else []
        top = sorted(nodes, key=lambda n: n.get("value", 0) or 0, reverse=True)[:5]
        return [{"name": n.get("label", ""), "value": n.get("value", 0)} for n in top]

    if not isinstance(data, list) or not data:
        return []

    value_field = encoding.get("y", "trial_count")

    clean = [
        {k: v for k, v in row.items() if k != "citations" and not isinstance(v, list)}
        for row in data
    ]

    # Sort descending by value so the LLM sees the most significant points first.
    if viz_type in ("bar_chart", "grouped_bar_chart"):
        clean.sort(key=lambda r: r.get(value_field, 0) or 0, reverse=True)

    return clean[:5]


async def generate_insight(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    final = state.get("final_response") or {}

    if final.get("status") != "visualization":
        return {"node_summary": "Skipped"}

    visualization = final.get("visualization", {})
    top = _top_data(visualization)

    if not top:
        logger.debug("generate_insight skipped request_id=%s no_data", rid)
        return {"node_summary": "Skipped — no chart data"}

    logger.debug(
        "generate_insight start request_id=%s chart_type=%s top_rows=%d",
        rid, visualization.get("type"), len(top),
    )

    try:
        from app.services.llm.client import LLMClient

        client = LLMClient()
        result: _InsightResponse = await client.complete_structured(
            prompt_id="insight_generator",
            response_model=_InsightResponse,
            variables={
                "query": state["query"],
                "title": visualization.get("title", ""),
                "chart_type": visualization.get("type", ""),
                "top_data": json.dumps(top, default=str),
            },
        )
        insight = result.insight.strip()
    except Exception as exc:
        logger.warning("generate_insight failed request_id=%s error=%s", rid, exc)
        return {"node_summary": "Insight unavailable"}

    if not insight:
        return {"node_summary": "Skipped — empty response"}

    logger.info("generate_insight ok request_id=%s chars=%d insight=%r", rid, len(insight), insight[:300])
    return {"final_response": {**final, "insight": insight}, "node_summary": f"Insight ({len(insight)} chars)"}
