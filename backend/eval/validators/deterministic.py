"""Deterministic validation checks for eval cases."""

from __future__ import annotations

from typing import Any


def _collect_citations(viz: dict[str, Any]) -> list:
    vtype = viz.get("type")
    data = viz.get("data", {})

    if vtype == "network_graph":
        citations = []
        for node in data.get("nodes", []):
            citations.extend(node.get("citations", []))
        for edge in data.get("edges", []):
            citations.extend(edge.get("citations", []))
        return citations

    if isinstance(data, list):
        citations = []
        for item in data:
            if isinstance(item, dict):
                citations.extend(item.get("citations", []))
        return citations

    return []


def validate(response: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    """Return a list of failure messages. Empty list means pass."""
    failures: list[str] = []

    actual_status = response.get("status")
    expected_status = expected.get("status")

    if actual_status != expected_status:
        failures.append(f"status: expected {expected_status!r}, got {actual_status!r}")
        # No point checking viz-specific fields if status is wrong
        return failures

    if actual_status == "message":
        expected_reason = expected.get("reason")
        if expected_reason:
            actual_reason = response.get("reason")
            if actual_reason != expected_reason:
                failures.append(
                    f"reason: expected {expected_reason!r}, got {actual_reason!r}"
                )
        # Ensure message field is non-empty
        if not response.get("message"):
            failures.append("message field is empty")
        return failures

    # status == "visualization"
    viz = response.get("visualization")
    if not viz:
        failures.append("visualization field missing")
        return failures

    actual_type = viz.get("type")
    expected_type = expected.get("visualization_type")
    expected_type_any = expected.get("visualization_type_any")
    if expected_type and actual_type != expected_type:
        failures.append(f"visualization.type: expected {expected_type!r}, got {actual_type!r}")
    elif expected_type_any and actual_type not in expected_type_any:
        failures.append(
            f"visualization.type: expected one of {expected_type_any!r}, got {actual_type!r}"
        )

    if actual_type == "network_graph":
        data = viz.get("data", {})
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        if expected.get("non_empty_nodes") and not nodes:
            failures.append("network_graph.data.nodes is empty")
        if expected.get("non_empty_edges") and not edges:
            failures.append("network_graph.data.edges is empty")
    else:
        data = viz.get("data", [])
        if expected.get("non_empty_data") and not data:
            failures.append("visualization.data is empty")

    if expected.get("has_citations"):
        cites = _collect_citations(viz)
        if not cites:
            failures.append("no citations found in visualization data")

    # Always check meta exists
    meta = response.get("meta")
    if not meta:
        failures.append("meta field missing")
    elif actual_status == "visualization":
        if not meta.get("source"):
            failures.append("meta.source is empty")
        if meta.get("records_retrieved", 0) == 0:
            failures.append("meta.records_retrieved is 0")

    return failures
