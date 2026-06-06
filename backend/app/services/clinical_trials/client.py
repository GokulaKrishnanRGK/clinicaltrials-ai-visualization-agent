"""Async ClinicalTrials.gov API v2 client with retry, backoff, and rate limiting."""

import asyncio
import random
import time
from collections.abc import Mapping
from typing import Any

import httpx

from app.logging_config import get_logger

logger = get_logger(__name__)

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})

# ClinicalTrials.gov allows ~1 request/second.
_MIN_INTERVAL_MS = 1_000


class ClinicalTrialsApiError(RuntimeError):
    """Raised when ClinicalTrials.gov cannot return a usable response."""


class ClinicalTrialsGovClient:
    """Async HTTP client for the ClinicalTrials.gov v2 API.

    Retries transient failures (network errors, timeouts, HTTP 429/5xx) with
    exponential backoff + jitter, and enforces a minimum inter-request interval
    so the client stays within the ~1 req/sec public rate limit.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://clinicaltrials.gov/api/v2",
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        base_backoff_ms: int = 1_000,
        max_backoff_ms: int = 30_000,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.base_backoff_ms = base_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self._last_request_at: float = 0.0

    async def search_studies(self, params: Mapping[str, str | int]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"Accept": "application/json"},
        ) as client:
            return await self._get_with_retry(client, "/studies", dict(params))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _throttle(self) -> None:
        """Block until the minimum inter-request interval has elapsed."""
        elapsed_ms = (time.monotonic() - self._last_request_at) * 1000
        wait_ms = _MIN_INTERVAL_MS - elapsed_ms
        if wait_ms > 0:
            await asyncio.sleep(wait_ms / 1000)
        self._last_request_at = time.monotonic()

    async def _get_with_retry(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        last_status: int | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                # Exponential backoff with ±25 % jitter (matches the Ref implementation).
                base_ms = min(self.base_backoff_ms * 2 ** (attempt - 1), self.max_backoff_ms)
                delay_ms = base_ms * (0.75 + 0.5 * random.random())
                logger.info(
                    "ct_api_retry path=%s attempt=%d delay_ms=%d last_status=%s",
                    path,
                    attempt,
                    round(delay_ms),
                    last_status,
                )
                await asyncio.sleep(delay_ms / 1000)

            await self._throttle()

            try:
                response = await client.get(path, params=params)
            except httpx.TimeoutException as exc:
                logger.warning("ct_api_timeout path=%s attempt=%d", path, attempt)
                last_error = exc
                continue
            except httpx.NetworkError as exc:
                logger.warning("ct_api_network_error path=%s attempt=%d error=%s", path, attempt, exc)
                last_error = exc
                continue

            if response.is_success:
                return self._parse_json(response)

            if response.status_code in _RETRYABLE_STATUSES:
                logger.warning(
                    "ct_api_retryable_status path=%s attempt=%d status=%d",
                    path,
                    attempt,
                    response.status_code,
                )
                last_status = response.status_code
                last_error = ClinicalTrialsApiError(f"HTTP {response.status_code}")
                continue

            # Non-retryable HTTP error (e.g. 400, 401, 403).
            raise ClinicalTrialsApiError(
                f"ClinicalTrials.gov returned HTTP {response.status_code}"
            )

        # All attempts exhausted.
        if last_status == 429:
            raise ClinicalTrialsApiError(
                f"Rate limited by ClinicalTrials.gov after {self.max_retries} retries"
            ) from last_error
        raise ClinicalTrialsApiError(
            f"ClinicalTrials.gov unavailable after {self.max_retries} retries"
        ) from last_error

    @staticmethod
    def _parse_json(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise ClinicalTrialsApiError("ClinicalTrials.gov returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ClinicalTrialsApiError("ClinicalTrials.gov returned an unexpected payload type")
        return payload
