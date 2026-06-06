"""Citation models for chart data and normalized records."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nct_id: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1, description="ClinicalTrials.gov JSON field path")
    value: Any
    excerpt: str | None = None
    brief_title: str | None = None
