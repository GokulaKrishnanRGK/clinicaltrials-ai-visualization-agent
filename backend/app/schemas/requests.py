"""Request schemas for visualization endpoints."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.enums import (
    NormalizedCountry,
    NormalizedStudyStatus,
    NormalizedTrialPhase,
    NormalizedVisualizationType,
)


class VisualizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(..., min_length=3)
    drug_name: str | None = None
    condition: str | None = None
    trial_phase: NormalizedTrialPhase | None = None
    sponsor: str | None = None
    country: NormalizedCountry | None = None
    status: NormalizedStudyStatus | None = None
    start_year: int | None = Field(default=None, ge=1900, le=2100)
    end_year: int | None = Field(default=None, ge=1900, le=2100)
    max_records: int = Field(default=500, ge=1, le=1000)
    preferred_visualization: NormalizedVisualizationType | None = None
    citation_limit: int = Field(default=10, ge=0, le=25)

    @model_validator(mode="after")
    def validate_year_range(self) -> "VisualizationRequest":
        if self.start_year is not None and self.end_year is not None:
            if self.start_year > self.end_year:
                raise ValueError("start_year must be less than or equal to end_year")
        return self
