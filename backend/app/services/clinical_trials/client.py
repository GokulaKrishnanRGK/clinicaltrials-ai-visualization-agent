"""Minimal async ClinicalTrials.gov API client."""

from collections.abc import Mapping
from typing import Any

import httpx


class ClinicalTrialsApiError(RuntimeError):
    """Raised when ClinicalTrials.gov cannot return a usable response."""


class ClinicalTrialsGovClient:
    def __init__(
        self,
        *,
        base_url: str = "https://clinicaltrials.gov/api/v2",
        timeout_seconds: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def search_studies(self, params: Mapping[str, str | int]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            follow_redirects=True,
        ) as client:
            try:
                response = await client.get("/studies", params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ClinicalTrialsApiError(
                    f"ClinicalTrials.gov returned HTTP {exc.response.status_code}"
                ) from exc
            except httpx.HTTPError as exc:
                raise ClinicalTrialsApiError("ClinicalTrials.gov request failed") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ClinicalTrialsApiError("ClinicalTrials.gov returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise ClinicalTrialsApiError("ClinicalTrials.gov returned an unexpected payload")

        return payload
