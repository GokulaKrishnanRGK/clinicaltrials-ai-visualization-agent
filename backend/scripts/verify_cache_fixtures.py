"""Validate cached fixture responses against the Milestone 2 response union."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.cache import get_cache_fixture_data_source


def main() -> None:
    data_source = get_cache_fixture_data_source()
    identifiers = data_source.list_identifiers()
    if len(identifiers) != 6:
        raise SystemExit(f"Expected 6 fixture identifiers, found {len(identifiers)}")

    for identifier in identifiers:
        fixture = data_source.get(identifier)
        print(f"validated {fixture.identifier}: {fixture.response.status}")

    cache_miss = data_source.cache_miss_response(
        request_id="verify-cache-miss",
        query="unavailable cache query",
    )
    if cache_miss.reason != "cache_miss" or "Switch to live mode" not in cache_miss.message:
        raise SystemExit("Cache miss response does not ask the user to switch to live mode")
    print("validated cache miss response")


if __name__ == "__main__":
    main()
