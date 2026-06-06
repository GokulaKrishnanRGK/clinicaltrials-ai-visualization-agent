"""POST /visualizations endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import TypeAdapter

from app.graph.pipeline import get_pipeline
from app.graph.state import GraphState
from app.schemas.requests import VisualizationRequest
from app.schemas.responses import VisualizationApiResponse

router = APIRouter()

_ResponseAdapter = TypeAdapter(VisualizationApiResponse)


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
        # Live mode defaults
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


@router.post("/visualizations", response_model=VisualizationApiResponse)
async def create_visualization(request: VisualizationRequest) -> Any:
    request_id = str(uuid.uuid4())
    initial_state = _build_initial_state(request, request_id)
    pipeline = get_pipeline()
    final_state: GraphState = await pipeline.ainvoke(initial_state)
    raw = final_state.get("final_response") or {}
    return _ResponseAdapter.validate_python(raw)
