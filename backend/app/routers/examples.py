from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/examples", tags=["examples"])


class ExampleRequest(BaseModel):
    query: str
    drug_name: str | None = None
    condition: str | None = None
    trial_phase: str | None = None
    sponsor: str | None = None
    country: str | None = None
    status: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    preferred_visualization: str | None = None


class ExampleSummary(BaseModel):
    id: str
    label: str
    request: ExampleRequest


_EXAMPLES: list[dict[str, Any]] = [
    {
        "id": "bar",
        "label": "Recruiting trials by country",
        "request": {
            "query": "Which countries have the most recruiting Alzheimer's trials?",
            "condition": "Alzheimer Disease",
            "status": "recruiting",
            "preferred_visualization": "bar_chart",
        },
    },
    {
        "id": "grouped",
        "label": "Phase by sponsor class",
        "request": {
            "query": "Compare Phase 2 and Phase 3 oncology trials by sponsor class.",
            "condition": "Neoplasms",
            "start_year": 2021,
            "end_year": 2025,
            "preferred_visualization": "grouped_bar_chart",
        },
    },
    {
        "id": "line",
        "label": "Enrollment trend",
        "request": {
            "query": "Show median enrollment for completed diabetes trials by year.",
            "condition": "Diabetes Mellitus",
            "status": "completed",
            "preferred_visualization": "line_chart",
        },
    },
    {
        "id": "time",
        "label": "Pembrolizumab starts",
        "request": {
            "query": "How many Pembrolizumab trials started each year since 2015?",
            "drug_name": "Pembrolizumab",
            "start_year": 2015,
            "preferred_visualization": "time_series",
        },
    },
    {
        "id": "network",
        "label": "Sponsor-condition network",
        "request": {
            "query": "Map sponsors connected to immunotherapy conditions.",
            "condition": "Immunotherapy",
            "preferred_visualization": "network_graph",
        },
    },
    {
        "id": "scatter",
        "label": "Trial complexity by year",
        "request": {
            "query": "Show how oncology trial intervention counts changed by start year.",
            "condition": "Neoplasms",
            "start_year": 2018,
            "end_year": 2024,
            "preferred_visualization": "scatter_chart",
        },
    },
    {
        "id": "histogram",
        "label": "COVID-19 trial year distribution",
        "request": {
            "query": "Show the distribution of COVID-19 trial registrations across year ranges.",
            "condition": "COVID-19",
            "preferred_visualization": "histogram",
        },
    },
    {
        "id": "compare_drugs",
        "label": "Drug comparison: Pembrolizumab vs Nivolumab",
        "request": {
            "query": "Compare Pembrolizumab vs Nivolumab phase distribution.",
            "preferred_visualization": "grouped_bar_chart",
        },
    },
    {
        "id": "compare_countries",
        "label": "Geographic comparison: US vs Germany oncology",
        "request": {
            "query": "Compare oncology trials in the United States vs Germany by phase.",
            "condition": "Neoplasms",
            "preferred_visualization": "grouped_bar_chart",
        },
    },
    {
        "id": "compare_status",
        "label": "Status comparison: recruiting vs completed Alzheimer's",
        "request": {
            "query": "Compare recruiting vs completed Alzheimer's trials by phase.",
            "condition": "Alzheimer Disease",
            "preferred_visualization": "grouped_bar_chart",
        },
    },
    {
        "id": "message",
        "label": "Insufficient data example",
        "request": {
            "query": "Find brand-new live trial updates for a rare intervention.",
            "preferred_visualization": "bar_chart",
        },
    },
]


@router.get("", response_model=list[ExampleSummary])
def get_examples() -> list[ExampleSummary]:
    return [ExampleSummary(**e) for e in _EXAMPLES]
