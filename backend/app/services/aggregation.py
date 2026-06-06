"""Deterministic aggregation utilities for trial record collections.

All aggregation is performed in Python — no LLM counting.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.schemas.citations import SourceCitation
from app.schemas.clinical_trials import NormalizedTrialRecord
from app.schemas.visualization import NetworkEdge, NetworkGraphData, NetworkNode


def _citation(record: NormalizedTrialRecord, field_key: str) -> SourceCitation | None:
    src = record.source_fields.get(field_key)
    if src is None:
        return None
    return SourceCitation(
        nct_id=record.nct_id,
        field=src.path,
        value=src.value,
        brief_title=record.brief_title,
    )


def _citations(
    records: list[NormalizedTrialRecord], field_key: str, limit: int
) -> list[SourceCitation]:
    if limit == 0:
        return []
    result: list[SourceCitation] = []
    for record in records:
        if len(result) >= limit:
            break
        cit = _citation(record, field_key)
        if cit is not None:
            result.append(cit)
    return result


def count_by_year(
    records: list[NormalizedTrialRecord],
    *,
    from_year: int | None = None,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by start year, sorted chronologically."""
    buckets: dict[int, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        if record.start_date is None:
            continue
        year = record.start_date.year
        if from_year is not None and year < from_year:
            continue
        buckets[year].append(record)
    return [
        {
            "start_year": year,
            "trial_count": len(recs),
            "citations": [c.model_dump() for c in _citations(recs, "start_date", citation_limit)],
        }
        for year, recs in sorted(buckets.items())
    ]


def count_by_country(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by country, sorted descending by count."""
    buckets: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        seen: set[str] = set()
        for country in record.countries:
            if country and country not in seen:
                buckets[country].append(record)
                seen.add(country)
    return [
        {
            "country": country,
            "trial_count": len(recs),
            "citations": [c.model_dump() for c in _citations(recs, "countries", citation_limit)],
        }
        for country, recs in sorted(buckets.items(), key=lambda x: -len(x[1]))
    ]


def count_by_phase(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by phase, sorted descending by count."""
    buckets: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        phase = "/".join(record.phases) if record.phases else "N/A"
        buckets[phase].append(record)
    return [
        {
            "phase": phase,
            "trial_count": len(recs),
            "citations": [c.model_dump() for c in _citations(recs, "phases", citation_limit)],
        }
        for phase, recs in sorted(buckets.items(), key=lambda x: -len(x[1]))
    ]


def count_by_status(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by overall status, sorted descending."""
    buckets: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        status = record.overall_status or "Unknown"
        buckets[status].append(record)
    return [
        {
            "status": status,
            "trial_count": len(recs),
            "citations": [
                c.model_dump() for c in _citations(recs, "overall_status", citation_limit)
            ],
        }
        for status, recs in sorted(buckets.items(), key=lambda x: -len(x[1]))
    ]


def count_by_phase_and_status(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials grouped by phase and status."""
    buckets: dict[tuple[str, str], list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        phase = "/".join(record.phases) if record.phases else "N/A"
        status = record.overall_status or "Unknown"
        buckets[(phase, status)].append(record)
    return [
        {
            "phase": phase,
            "status": status,
            "trial_count": len(recs),
            "citations": [
                c.model_dump() for c in _citations(recs, "overall_status", citation_limit)
            ],
        }
        for (phase, status), recs in sorted(buckets.items(), key=lambda x: -len(x[1]))
    ]


def count_by_sponsor(
    records: list[NormalizedTrialRecord],
    *,
    top_n: int = 20,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by lead sponsor, top N descending."""
    buckets: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        sponsor = record.lead_sponsor or "Unknown"
        buckets[sponsor].append(record)
    return [
        {
            "sponsor": sponsor,
            "trial_count": len(recs),
            "citations": [c.model_dump() for c in _citations(recs, "lead_sponsor", citation_limit)],
        }
        for sponsor, recs in sorted(buckets.items(), key=lambda x: -len(x[1]))[:top_n]
    ]


def count_by_phase_per_drug(
    records: list[dict[str, Any]],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Count trials by (phase, comparison_drug) for drug-vs-drug queries.

    Records must be plain dicts with a `comparison_drug` key (set by execute_tools).
    """
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        phase = "/".join(record.get("phases") or []) or "N/A"
        drug = record.get("comparison_drug") or "Unknown"
        buckets[(phase, drug)].append(record)
    return [
        {
            "phase": phase,
            "drug_name": drug,
            "trial_count": len(recs),
            "citations": [
                {
                    "nct_id": r.get("nct_id", ""),
                    "field": "interventions",
                    "value": drug,
                    "brief_title": r.get("brief_title"),
                }
                for r in recs[:citation_limit]
            ] if citation_limit else [],
        }
        for (phase, drug), recs in sorted(buckets.items(), key=lambda x: -len(x[1]))
    ]


def build_drug_sponsor_network(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> NetworkGraphData:
    """Build a drug→sponsor network from trial records."""
    drug_recs: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    sponsor_recs: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    edge_recs: dict[tuple[str, str], list[NormalizedTrialRecord]] = defaultdict(list)

    for record in records:
        if not record.lead_sponsor:
            continue
        sponsor_id = "sponsor_" + record.lead_sponsor.lower().replace(" ", "_")[:30]
        sponsor_recs[sponsor_id].append(record)
        for drug in record.interventions[:5]:
            if not drug:
                continue
            drug_id = "drug_" + drug.lower().replace(" ", "_")[:30]
            drug_recs[drug_id].append(record)
            edge_recs[(drug_id, sponsor_id)].append(record)

    nodes: list[NetworkNode] = [
        NetworkNode(
            id=drug_id,
            label=recs[0].interventions[0],
            type="drug",
            value=len(recs),
            citations=_citations(recs, "interventions", citation_limit),
        )
        for drug_id, recs in drug_recs.items()
        if recs[0].interventions
    ] + [
        NetworkNode(
            id=sponsor_id,
            label=recs[0].lead_sponsor or sponsor_id,
            type="sponsor",
            value=len(recs),
            citations=_citations(recs, "lead_sponsor", citation_limit),
        )
        for sponsor_id, recs in sponsor_recs.items()
    ]

    edges: list[NetworkEdge] = [
        NetworkEdge(
            source=drug_id,
            target=sponsor_id,
            weight=len(recs),
            relation="sponsors",
            citations=_citations(recs, "interventions", citation_limit),
        )
        for (drug_id, sponsor_id), recs in edge_recs.items()
    ]

    return NetworkGraphData(nodes=nodes, edges=edges)


def scatter_interventions_by_year(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Per start-year: avg intervention count and trial count for scatter plot."""
    buckets: dict[int, list[NormalizedTrialRecord]] = defaultdict(list)
    for record in records:
        if record.start_date is None:
            continue
        buckets[record.start_date.year].append(record)
    return [
        {
            "start_year": year,
            "avg_interventions": round(
                sum(len(r.interventions) for r in recs) / len(recs), 1
            ),
            "trial_count": len(recs),
            "citations": [
                c.model_dump() for c in _citations(recs, "interventions", citation_limit)
            ],
        }
        for year, recs in sorted(buckets.items())
    ]


def histogram_start_years(
    records: list[NormalizedTrialRecord],
    *,
    bins: int = 8,
    citation_limit: int = 10,
) -> list[dict[str, Any]]:
    """Histogram of trial start years across equal-width year bins."""
    dated = [(r.start_date.year, r) for r in records if r.start_date is not None]
    if not dated:
        return []
    all_years = [y for y, _ in dated]
    min_year, max_year = min(all_years), max(all_years)
    span = max(1, max_year - min_year + 1)
    bin_size = max(1, (span + bins - 1) // bins)

    bin_buckets: dict[int, list[NormalizedTrialRecord]] = defaultdict(list)
    for year, record in dated:
        bin_start = min_year + ((year - min_year) // bin_size) * bin_size
        bin_buckets[bin_start].append(record)

    return [
        {
            "range_label": (
                str(bin_start)
                if bin_size == 1
                else f"{bin_start}–{min(bin_start + bin_size - 1, max_year)}"
            ),
            "min_year": bin_start,
            "max_year": min(bin_start + bin_size - 1, max_year),
            "trial_count": len(recs),
            "citations": [c.model_dump() for c in _citations(recs, "start_date", citation_limit)],
        }
        for bin_start, recs in sorted(bin_buckets.items())
    ]


def build_drug_cooccurrence_network(
    records: list[NormalizedTrialRecord],
    *,
    citation_limit: int = 10,
) -> NetworkGraphData:
    """Build a drug co-occurrence network from trial records."""
    drug_recs: dict[str, list[NormalizedTrialRecord]] = defaultdict(list)
    edge_recs: dict[frozenset[str], list[NormalizedTrialRecord]] = defaultdict(list)

    for record in records:
        drugs = [d for d in record.interventions if d][:8]
        drug_ids = ["drug_" + d.lower().replace(" ", "_")[:30] for d in drugs]
        for drug_id in drug_ids:
            drug_recs[drug_id].append(record)
        if len(drug_ids) >= 2:
            for i, d1 in enumerate(drug_ids):
                for d2 in drug_ids[i + 1 :]:
                    edge_recs[frozenset([d1, d2])].append(record)

    drug_labels: dict[str, str] = {}
    for record in records:
        for drug in record.interventions[:8]:
            if drug:
                drug_id = "drug_" + drug.lower().replace(" ", "_")[:30]
                drug_labels.setdefault(drug_id, drug)

    nodes: list[NetworkNode] = [
        NetworkNode(
            id=drug_id,
            label=drug_labels.get(drug_id, drug_id),
            type="drug",
            value=len(recs),
            citations=_citations(recs, "interventions", citation_limit),
        )
        for drug_id, recs in drug_recs.items()
    ]

    edges: list[NetworkEdge] = [
        NetworkEdge(
            source=sorted(pair)[0],
            target=sorted(pair)[1],
            weight=len(recs),
            relation="co_occurs_with",
            citations=_citations(recs, "interventions", citation_limit),
        )
        for pair, recs in edge_recs.items()
    ]

    return NetworkGraphData(nodes=nodes, edges=edges)
