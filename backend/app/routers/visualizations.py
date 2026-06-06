from __future__ import annotations

import json
import time
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import TypeAdapter

from app.graph.pipeline import get_pipeline
from app.graph.state import GraphState
from app.schemas.requests import VisualizationRequest
from app.schemas.responses import VisualizationApiResponse

router = APIRouter()

_ResponseAdapter = TypeAdapter(VisualizationApiResponse)

_TRACKED_NODES = {
    "cache_lookup",
    "interpret_question",
    "create_retrieval_plan",
    "execute_tools",
    "assess_data_sufficiency",
    "repair_plan",
    "aggregate_data",
    "generate_visualization_spec",
    "validate_response",
    "message_insufficient",
}


def _build_initial_state(request: VisualizationRequest, request_id: str) -> GraphState:
    return GraphState(
        request_id=request_id,
        query=request.query,
        data_mode=request.data_mode,
        max_records=request.max_records,
        citation_limit=request.citation_limit,
        preferred_visualization=(
            request.preferred_visualization.value if request.preferred_visualization else None
        ),
        drug_name=request.drug_name,
        condition=request.condition,
        trial_phase=request.trial_phase.value if request.trial_phase else None,
        sponsor=request.sponsor,
        country=request.country,
        status=request.status.value if request.status else None,
        start_year=request.start_year,
        end_year=request.end_year,
        interpreted={},
        assumptions=[],
        warnings=[],
        retrieval_params={},
        records=[],
        records_retrieved=0,
        tool_warnings=[],
        repair_count=0,
        agg_type=None,
        agg_data=None,
        final_response=None,
    )


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/visualizations", response_model=VisualizationApiResponse)
async def create_visualization(request: VisualizationRequest) -> Any:
    request_id = str(uuid.uuid4())
    initial_state = _build_initial_state(request, request_id)
    pipeline = get_pipeline()
    final_state: GraphState = await pipeline.ainvoke(initial_state)
    raw = final_state.get("final_response") or {}
    return _ResponseAdapter.validate_python(raw)


@router.post("/visualizations/stream")
async def stream_visualization(request: VisualizationRequest) -> StreamingResponse:
    async def generate():
        initial_state = _build_initial_state(request, str(uuid.uuid4()))
        pipeline = get_pipeline()
        node_start_times: dict[str, float] = {}
        node_start_counts: dict[str, int] = {}

        async for event in pipeline.astream_events(initial_state, version="v2"):
            ev_type: str = event["event"]
            name: str = event.get("name", "")

            if ev_type == "on_chain_start" and name in _TRACKED_NODES:
                node_start_times[name] = time.monotonic()
                count = node_start_counts.get(name, 0) + 1
                node_start_counts[name] = count
                if count > 1:
                    yield _sse({"type": "node_retry", "node": name, "attempt": count})
                else:
                    yield _sse({"type": "node_start", "node": name})

            elif ev_type == "on_chain_end" and name in _TRACKED_NODES:
                elapsed = time.monotonic() - node_start_times.get(name, time.monotonic())
                duration_ms = int(elapsed * 1000)
                yield _sse({"type": "node_success", "node": name, "duration_ms": duration_ms})

            elif ev_type == "on_chain_error" and name in _TRACKED_NODES:
                error = str(event.get("data", {}).get("error", "unknown error"))
                yield _sse({"type": "node_error", "node": name, "error": error})

            elif ev_type == "on_chain_end" and name == "LangGraph":
                output = event.get("data", {}).get("output", {})
                raw = output.get("final_response") or {}
                try:
                    response_data = _ResponseAdapter.validate_python(raw).model_dump(mode="json")
                except Exception:
                    response_data = raw
                yield _sse({"type": "final_response", "response": response_data})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
