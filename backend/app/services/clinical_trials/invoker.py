"""Typed in-process ClinicalTrials.gov tool boundary."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.clinical_trials import NormalizedTrialRecord
from app.schemas.requests import VisualizationRequest
from app.schemas.responses import ResponseMetadata
from app.services.clinical_trials.client import ClinicalTrialsApiError, ClinicalTrialsGovClient
from app.services.clinical_trials.normalizer import normalize_study


class ClinicalTrialsToolError(RuntimeError):
    """Raised when the tool boundary cannot satisfy a request."""


class ClinicalTrialsToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_mode: Literal["cache", "live"]
    filters: dict[str, str | int] = Field(default_factory=dict)
    records_retrieved: int = Field(..., ge=0)
    records: list[NormalizedTrialRecord] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def records_used(self) -> int:
        return len(self.records)

    def to_response_metadata(self) -> ResponseMetadata:
        return ResponseMetadata(
            data_mode=self.data_mode,
            filters=self.filters,
            records_retrieved=self.records_retrieved,
            records_used=self.records_used,
            generated_at=datetime.now(UTC),
        )


class ClinicalTrialsToolInvoker:
    """Fetch and normalize ClinicalTrials.gov studies for downstream graph nodes."""

    def __init__(self, client: ClinicalTrialsGovClient | None = None) -> None:
        self.client = client or ClinicalTrialsGovClient()

    async def invoke(self, request: VisualizationRequest) -> ClinicalTrialsToolResult:
        filters = self._filters_from_request(request)
        if request.data_mode == "cache":
            return ClinicalTrialsToolResult(
                data_mode=request.data_mode,
                filters=filters,
                records_retrieved=0,
                records=[],
                warnings=["Cache mode is not implemented in the ClinicalTrials.gov tool boundary."],
            )

        params = self._params_from_filters(filters, request.max_records)
        try:
            payload = await self.client.search_studies(params)
        except ClinicalTrialsApiError as exc:
            raise ClinicalTrialsToolError(str(exc)) from exc

        studies = payload.get("studies", [])
        if not isinstance(studies, list):
            raise ClinicalTrialsToolError("ClinicalTrials.gov returned invalid studies data")

        records = [
            record
            for study in studies
            if isinstance(study, dict)
            for record in [normalize_study(study)]
            if record is not None
        ]
        warnings = []
        if len(records) < len(studies):
            warnings.append("Some ClinicalTrials.gov studies were skipped during normalization.")
        if payload.get("nextPageToken"):
            warnings.append(
                "Additional ClinicalTrials.gov records are available beyond max_records."
            )

        return ClinicalTrialsToolResult(
            data_mode=request.data_mode,
            filters=filters,
            records_retrieved=len(studies),
            records=records,
            warnings=warnings,
        )

    def _filters_from_request(self, request: VisualizationRequest) -> dict[str, str | int]:
        filters: dict[str, str | int] = {
            "query": request.query,
            "max_records": request.max_records,
        }
        optional_filters: dict[str, str | int | None] = {
            "drug_name": request.drug_name,
            "condition": request.condition,
            "trial_phase": request.trial_phase.value if request.trial_phase else None,
            "sponsor": request.sponsor,
            "country": request.country,
            "status": request.status.value if request.status else None,
            "start_year": request.start_year,
            "end_year": request.end_year,
        }
        filters.update(
            {
                key: value
                for key, value in optional_filters.items()
                if value is not None and value != ""
            }
        )
        return filters

    def _params_from_filters(
        self, filters: dict[str, str | int], max_records: int
    ) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            "format": "json",
            "pageSize": max_records,
            "query.term": str(filters["query"]),
        }
        if "condition" in filters:
            params["query.cond"] = str(filters["condition"])
        if "drug_name" in filters:
            params["query.intr"] = str(filters["drug_name"])
        if "sponsor" in filters:
            params["query.spons"] = str(filters["sponsor"])
        if "country" in filters:
            params["query.locn"] = str(filters["country"])
        if "status" in filters:
            params["filter.overallStatus"] = str(filters["status"])

        advanced_filters = self._advanced_filters(filters)
        if advanced_filters:
            params["filter.advanced"] = " AND ".join(advanced_filters)

        return params

    def _advanced_filters(self, filters: dict[str, str | int]) -> list[str]:
        advanced_filters: list[str] = []
        if "trial_phase" in filters:
            advanced_filters.append(f"AREA[Phase]{filters['trial_phase']}")

        start_year = filters.get("start_year")
        end_year = filters.get("end_year")
        if isinstance(start_year, int) or isinstance(end_year, int):
            start_date = f"{start_year}-01-01" if isinstance(start_year, int) else "MIN"
            end_date = f"{end_year}-12-31" if isinstance(end_year, int) else "MAX"
            advanced_filters.append(f"AREA[StartDate]RANGE[{start_date},{end_date}]")

        return advanced_filters
