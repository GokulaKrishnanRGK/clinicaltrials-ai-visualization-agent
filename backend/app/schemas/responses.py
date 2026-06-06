"""Response schemas for visualization endpoints."""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.visualization import VisualizationSpec


class ResponseMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["clinicaltrials.gov"] = "clinicaltrials.gov"
    filters: dict[str, Any] = Field(default_factory=dict)
    records_retrieved: int = Field(..., ge=0)
    records_used: int = Field(..., ge=0)
    generated_at: datetime


class VisualizationSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["visualization"] = "visualization"
    request_id: str = Field(..., min_length=1)
    visualization: VisualizationSpec
    meta: ResponseMetadata
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    insight: str | None = None


class VisualizationMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["message"] = "message"
    request_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    reason: Literal[
        "vague_query",
        "unsupported_query",
        "llm_failure",
        "api_failure",
        "insufficient_data",
        "validation_failure",
    ]
    suggested_queries: list[str] = Field(default_factory=list)
    meta: ResponseMetadata | None = None


VisualizationApiResponse = Annotated[
    VisualizationSuccessResponse | VisualizationMessageResponse,
    Field(discriminator="status"),
]
