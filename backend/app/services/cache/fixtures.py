"""Load canned cache-mode responses for graph/API integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.schemas.responses import VisualizationApiResponse, VisualizationMessageResponse

ResponseAdapter = TypeAdapter(VisualizationApiResponse)


class CacheFixtureNotFoundError(KeyError):
    """Raised when a requested fixture identifier is not present."""


@dataclass(frozen=True)
class CachedFixture:
    identifier: str
    title: str
    description: str
    query: str
    response: VisualizationApiResponse


class CacheFixtureDataSource:
    def __init__(self, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = fixture_dir or self._default_fixture_dir()
        self._manifest = self._load_json(self.fixture_dir / "manifest.json")

    @staticmethod
    def _default_fixture_dir() -> Path:
        return Path(__file__).resolve().parents[3] / "data" / "fixtures"

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as fixture_file:
            data = json.load(fixture_file)
        if not isinstance(data, dict):
            raise ValueError(f"Expected object fixture JSON at {path}")
        return data

    def list_identifiers(self) -> list[str]:
        fixtures = self._manifest.get("fixtures", [])
        return [fixture["id"] for fixture in fixtures]

    def get(self, identifier: str) -> CachedFixture:
        fixture_meta = self._fixture_meta(identifier)
        response_data = self._load_json(self.fixture_dir / fixture_meta["file"])
        response = ResponseAdapter.validate_python(response_data)
        return CachedFixture(
            identifier=fixture_meta["id"],
            title=fixture_meta["title"],
            description=fixture_meta["description"],
            query=fixture_meta["query"],
            response=response,
        )

    def get_response(self, identifier: str) -> VisualizationApiResponse:
        return self.get(identifier).response

    def cache_miss_response(
        self,
        request_id: str,
        query: str,
        *,
        suggested_limit: int = 3,
    ) -> VisualizationMessageResponse:
        suggested_queries = [
            fixture["query"] for fixture in self._manifest.get("fixtures", [])[:suggested_limit]
        ]
        return VisualizationMessageResponse(
            request_id=request_id,
            message=(
                "This query is not available in cache mode. Switch to live mode "
                "to query ClinicalTrials.gov directly, or choose one of the cached examples."
            ),
            reason="cache_miss",
            suggested_queries=suggested_queries,
            meta={
                "data_mode": "cache",
                "filters": {"query": query},
                "records_retrieved": 0,
                "records_used": 0,
                "generated_at": datetime.now(UTC),
            },
        )

    def _fixture_meta(self, identifier: str) -> dict[str, Any]:
        for fixture in self._manifest.get("fixtures", []):
            if fixture.get("id") == identifier:
                return fixture
        raise CacheFixtureNotFoundError(identifier)


@lru_cache
def get_cache_fixture_data_source() -> CacheFixtureDataSource:
    return CacheFixtureDataSource()
