"""Retrieval plan schema — output of the plan_tool_calls node."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

AGG_TYPES = frozenset(
    {
        "by_year",
        "by_phase",
        "by_status",
        "by_country",
        "by_sponsor",
        "by_phase_and_status",
        "by_phase_per_label",
        "drug_sponsor_network",
        "drug_cooccurrence_network",
        "drug_condition_network",
        "scatter_by_year",
        "histogram_by_year",
    }
)


class FetchSpec(BaseModel):
    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1)
    drug_name: str | None = None
    condition: str | None = None
    country: str | None = None
    status: str | None = None
    trial_phase: str | None = None
    sponsor: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    max_records: int = Field(default=200, ge=1, le=500)


class RetrievalPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    calls: list[FetchSpec] = Field(..., min_length=1, max_length=4)
    agg_type: str = Field(..., description="One of the known aggregation type strings.")
