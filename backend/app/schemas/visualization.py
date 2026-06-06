"""Frontend-ready visualization contract models."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.citations import SourceCitation
from app.schemas.enums import VisualizationType


class EChartsRenderHints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x_axis_label: str | None = None
    y_axis_label: str | None = None
    series_name: str | None = None
    group_field: str | None = None
    category_field: str | None = None
    value_field: str | None = None
    tooltip_fields: list[str] = Field(default_factory=list)
    sort: str | None = Field(
        default=None, description="Frontend hint such as asc, desc, or chronological"
    )
    legend: bool = True


class ChartDatum(BaseModel):
    model_config = ConfigDict(extra="allow")

    citations: list[SourceCitation] = Field(default_factory=list)


class NetworkNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    type: Literal["drug", "sponsor", "condition", "trial", "site", "country"]
    value: int | float | None = None
    citations: list[SourceCitation] = Field(default_factory=list)


class NetworkEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    weight: int | float = Field(..., ge=0)
    relation: Literal["sponsors", "co_occurs_with", "studies"]
    citations: list[SourceCitation] = Field(default_factory=list)


class NetworkGraphData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[NetworkNode]
    edges: list[NetworkEdge]


class BaseVisualizationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str | None = None
    encoding: dict[str, Any]
    render_hints: EChartsRenderHints | None = None

    @property
    def is_network(self) -> bool:
        return False


class ChartVisualizationSpec(BaseVisualizationSpec):
    type: Literal[
        VisualizationType.BAR_CHART,
        VisualizationType.GROUPED_BAR_CHART,
        VisualizationType.LINE_CHART,
        VisualizationType.TIME_SERIES,
    ]
    data: list[ChartDatum]


class NetworkVisualizationSpec(BaseVisualizationSpec):
    type: Literal[VisualizationType.NETWORK_GRAPH]
    data: NetworkGraphData

    @property
    def is_network(self) -> bool:
        return True


VisualizationSpec = Annotated[
    ChartVisualizationSpec | NetworkVisualizationSpec,
    Field(discriminator="type"),
]
