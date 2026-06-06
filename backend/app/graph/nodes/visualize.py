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
    "by_sponsor": VisualizationType.BAR_CHART,
    "drug_sponsor_network": VisualizationType.NETWORK_GRAPH,
    "drug_cooccurrence_network": VisualizationType.NETWORK_GRAPH,
}

_CHART_TITLES: dict[str, str] = {
    "by_year": "Trials by Start Year",
    "by_country": "Trials by Country",
    "by_phase": "Trials by Phase",
    "by_status": "Trials by Status",
    "by_phase_and_status": "Trials by Phase and Status",
    "by_sponsor": "Trials by Sponsor",
    "drug_sponsor_network": "Drug–Sponsor Network",
    "drug_cooccurrence_network": "Drug Co-occurrence Network",
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
    title = _CHART_TITLES.get(agg_type, state["query"][:80])
    logger.debug("generate_visualization_spec request_id=%s agg_type=%s title=%r", rid, agg_type, title)

    if agg_type in ("drug_sponsor_network", "drug_cooccurrence_network"):
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
    else:
        default_config = (
            {"x": "label", "y": "value"},
            EChartsRenderHints(category_field="label", value_field="value"),
        )
        encoding, render_hints = _CHART_CONFIGS.get(agg_type, default_config)
        spec = ChartVisualizationSpec(
            type=_AGG_TYPE_TO_VIZ[agg_type],
            title=title,
            encoding=encoding,
            render_hints=render_hints,
            data=[ChartDatum.model_validate(d) for d in agg_data],
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
        "generate_visualization_spec complete request_id=%s viz_type=%s records_used=%d",
        rid,
        spec.type.value,
        len(records),
    )
    return {"final_response": response.model_dump(mode="json")}
