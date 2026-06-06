"""Internal ClinicalTrials.gov record schemas shared by future tools and citations."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., min_length=1)
    value: Any


class TrialLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    facility: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class NormalizedTrialRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nct_id: str = Field(..., min_length=1)
    brief_title: str | None = None
    official_title: str | None = None
    overall_status: str | None = None
    phases: list[str] = Field(default_factory=list)
    study_type: str | None = None
    start_date: date | None = None
    conditions: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)
    lead_sponsor: str | None = None
    sponsor_class: str | None = None
    locations: list[TrialLocation] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    source_fields: dict[str, SourceField] = Field(default_factory=dict)
