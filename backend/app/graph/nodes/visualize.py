from __future__ import annotations

from typing import Any

from app.graph.nodes._helpers import build_meta
from app.graph.state import GraphState
from app.logging_config import get_logger

logger = get_logger(__name__)
from app.schemas.enums import VisualizationType
from app.schemas.responses import VisualizationSuccessResponse
from app.schemas.visualization import (
    ChartDatum,
    ChartVisualizationSpec,
    EChartsRenderHints,
    NetworkVisualizationSpec,
)

_AGG_TYPE_TO_VIZ: dict[str, VisualizationType] = {
    "by_year": VisualizationType.TIME_SERIES,
    "by_country": VisualizationType.BAR_CHART,
    "by_phase": VisualizationType.BAR_CHART,
    "by_status": VisualizationType.BAR_CHART,
    "by_phase_and_status": VisualizationType.GROUPED_BAR_CHART,
    "by_phase_per_label": VisualizationType.GROUPED_BAR_CHART,
    "by_sponsor": VisualizationType.BAR_CHART,
    "scatter_by_year": VisualizationType.SCATTER_CHART,
    "histogram_by_year": VisualizationType.HISTOGRAM,
    "drug_sponsor_network": VisualizationType.NETWORK_GRAPH,
    "drug_cooccurrence_network": VisualizationType.NETWORK_GRAPH,
    "drug_condition_network": VisualizationType.NETWORK_GRAPH,
}

_CHART_TITLES: dict[str, str] = {
    "by_year": "Trials by Start Year",
    "by_country": "Trials by Country",
    "by_phase": "Trials by Phase",
    "by_status": "Trials by Status",
    "by_phase_and_status": "Trials by Phase and Status",
    "by_phase_per_label": "Trials by Phase per Group",
    "by_sponsor": "Trials by Sponsor",
    "scatter_by_year": "Trial Interventions by Start Year",
    "histogram_by_year": "Trial Registrations by Year Range",
    "drug_sponsor_network": "Drug–Sponsor Network",
    "drug_cooccurrence_network": "Drug Co-occurrence Network",
    "drug_condition_network": "Drug–Condition Network",
}

_CHART_CONFIGS: dict[str, tuple[dict[str, str], EChartsRenderHints]] = {
    "by_year": (
        {"x": "start_year", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Year",
            y_axis_label="Trials",
            category_field="start_year",
            value_field="trial_count",
            sort="chronological",
            legend=False,
        ),
    ),
    "by_country": (
        {"x": "country", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Country",
            y_axis_label="Trials",
            category_field="country",
            value_field="trial_count",
            sort="desc",
            legend=False,
        ),
    ),
    "by_phase": (
        {"x": "phase", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Phase",
            y_axis_label="Trials",
            category_field="phase",
            value_field="trial_count",
            legend=False,
        ),
    ),
    "by_status": (
        {"x": "status", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Status",
            y_axis_label="Trials",
            category_field="status",
            value_field="trial_count",
            legend=False,
        ),
    ),
    "by_phase_and_status": (
        {"x": "phase", "y": "trial_count", "group": "status"},
        EChartsRenderHints(
            x_axis_label="Phase",
            y_axis_label="Trials",
            category_field="phase",
            value_field="trial_count",
            group_field="status",
            legend=True,
        ),
    ),
    "by_phase_per_label": (
        {"x": "phase", "y": "trial_count", "group": "label"},
        EChartsRenderHints(
            x_axis_label="Phase",
            y_axis_label="Trials",
            category_field="phase",
            value_field="trial_count",
            group_field="label",
            legend=True,
        ),
    ),
    "by_sponsor": (
        {"x": "sponsor", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Sponsor",
            y_axis_label="Trials",
            category_field="sponsor",
            value_field="trial_count",
            sort="desc",
            legend=False,
        ),
    ),
    "scatter_by_year": (
        {"x": "start_year", "y": "avg_interventions"},
        EChartsRenderHints(
            x_axis_label="Start Year",
            y_axis_label="Avg Interventions per Trial",
            category_field="start_year",
            value_field="avg_interventions",
            sort="chronological",
            legend=False,
            tooltip_fields=["start_year", "avg_interventions", "trial_count"],
        ),
    ),
    "histogram_by_year": (
        {"x": "range_label", "y": "trial_count"},
        EChartsRenderHints(
            x_axis_label="Year Range",
            y_axis_label="Trials Registered",
            category_field="range_label",
            value_field="trial_count",
            legend=False,
        ),
    ),
}

_NETWORK_ENCODING: dict[str, str] = {
    "node_id": "id",
    "node_label": "label",
    "edge_source": "source",
    "edge_target": "target",
    "edge_weight": "weight",
}


def generate_visualization_spec(state: GraphState) -> dict[str, Any]:
    rid = state["request_id"]
    agg_type = state["agg_type"]
    agg_data = state["agg_data"]
    agg_rows = len(agg_data) if isinstance(agg_data, list) else 1
    title = _CHART_TITLES.get(agg_type, state["query"][:80])
    logger.debug(
        "generate_visualization_spec input request_id=%s agg_type=%s agg_rows=%d title=%r",
        rid,
        agg_type,
        agg_rows,
        title,
    )

    if agg_type in ("drug_sponsor_network", "drug_cooccurrence_network", "drug_condition_network"):
        spec = NetworkVisualizationSpec(
            type=VisualizationType.NETWORK_GRAPH,
            title=title,
            encoding=_NETWORK_ENCODING,
            render_hints=EChartsRenderHints(
                series_name="Study relationships",
                tooltip_fields=["label", "type", "value"],
                legend=True,
            ),
            data=agg_data,
        )
        logger.debug(
            "generate_visualization_spec data_sample request_id=%s encoding=%s "
            "nodes=%d edges=%d",
            rid,
            _NETWORK_ENCODING,
            len(agg_data.nodes) if hasattr(agg_data, "nodes") else 0,
            len(agg_data.edges) if hasattr(agg_data, "edges") else 0,
        )
    else:
        default_config = (
            {"x": "label", "y": "value"},
            EChartsRenderHints(category_field="label", value_field="value"),
        )
        encoding, render_hints = _CHART_CONFIGS.get(agg_type, default_config)
        viz_type = _AGG_TYPE_TO_VIZ.get(agg_type, VisualizationType.BAR_CHART)
        spec = ChartVisualizationSpec(
            type=viz_type,
            title=title,
            encoding=encoding,
            render_hints=render_hints,
            data=[ChartDatum.model_validate(d) for d in agg_data],
        )
        if logger.isEnabledFor(10) and isinstance(agg_data, list):
            data_sample = [
                {k: v for k, v in row.items() if k != "citations"}
                for row in agg_data[:2]
            ]
            logger.debug(
                "generate_visualization_spec data_sample request_id=%s encoding=%s sample=%s",
                rid,
                encoding,
                data_sample,
            )

    records = state.get("records", [])
    meta = build_meta(
        state,
        records_retrieved=state.get("records_retrieved", 0),
        records_used=len(records),
    )
    response = VisualizationSuccessResponse(
        request_id=state["request_id"],
        visualization=spec,
        meta=meta,
        warnings=list(state.get("warnings", [])) + list(state.get("tool_warnings", [])),
        assumptions=state.get("assumptions", []),
    )
    logger.info(
        "generate_visualization_spec output request_id=%s viz_type=%s records_used=%d title=%r",
        rid,
        spec.type.value,
        len(records),
        title,
    )
    node_summary = f"{spec.type.value.replace('_', ' ')}: {title}"
    return {"final_response": response.model_dump(mode="json"), "node_summary": node_summary}
