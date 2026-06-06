"""Public API enum values and normalization helpers."""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import BeforeValidator, WithJsonSchema


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


class TrialPhase(StrEnum):
    NOT_APPLICABLE = "NA"
    EARLY_PHASE_1 = "EARLY_PHASE1"
    PHASE_1 = "PHASE1"
    PHASE_2 = "PHASE2"
    PHASE_3 = "PHASE3"
    PHASE_4 = "PHASE4"


TRIAL_PHASE_ALIASES: dict[str, TrialPhase] = {
    "na": TrialPhase.NOT_APPLICABLE,
    "n_a": TrialPhase.NOT_APPLICABLE,
    "not_applicable": TrialPhase.NOT_APPLICABLE,
    "early_phase_1": TrialPhase.EARLY_PHASE_1,
    "early_phase1": TrialPhase.EARLY_PHASE_1,
    "early_phase": TrialPhase.EARLY_PHASE_1,
    "phase_1": TrialPhase.PHASE_1,
    "phase1": TrialPhase.PHASE_1,
    "phase_i": TrialPhase.PHASE_1,
    "phase_2": TrialPhase.PHASE_2,
    "phase2": TrialPhase.PHASE_2,
    "phase_ii": TrialPhase.PHASE_2,
    "phase_3": TrialPhase.PHASE_3,
    "phase3": TrialPhase.PHASE_3,
    "phase_iii": TrialPhase.PHASE_3,
    "phase_4": TrialPhase.PHASE_4,
    "phase4": TrialPhase.PHASE_4,
    "phase_iv": TrialPhase.PHASE_4,
}


class StudyStatus(StrEnum):
    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    COMPLETED = "COMPLETED"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    RECRUITING = "RECRUITING"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    WITHDRAWN = "WITHDRAWN"
    AVAILABLE = "AVAILABLE"
    NO_LONGER_AVAILABLE = "NO_LONGER_AVAILABLE"
    TEMPORARILY_NOT_AVAILABLE = "TEMPORARILY_NOT_AVAILABLE"
    APPROVED_FOR_MARKETING = "APPROVED_FOR_MARKETING"
    WITHHELD = "WITHHELD"
    UNKNOWN = "UNKNOWN"


STUDY_STATUS_ALIASES: dict[str, StudyStatus] = {
    _normalize_key(status.name): status for status in StudyStatus
} | {_normalize_key(status.value): status for status in StudyStatus} | {
    # Common LLM mistakes — map "active" to ACTIVE_NOT_RECRUITING (closest match)
    "active": StudyStatus.ACTIVE_NOT_RECRUITING,
    "open": StudyStatus.RECRUITING,
    "closed": StudyStatus.COMPLETED,
    "ongoing": StudyStatus.ACTIVE_NOT_RECRUITING,
}


class VisualizationType(StrEnum):
    BAR_CHART = "bar_chart"
    GROUPED_BAR_CHART = "grouped_bar_chart"
    LINE_CHART = "line_chart"
    TIME_SERIES = "time_series"
    NETWORK_GRAPH = "network_graph"
    SCATTER_CHART = "scatter_chart"
    HISTOGRAM = "histogram"


VISUALIZATION_TYPE_ALIASES: dict[str, VisualizationType] = {
    "bar": VisualizationType.BAR_CHART,
    "bar_chart": VisualizationType.BAR_CHART,
    "bar_graph": VisualizationType.BAR_CHART,
    "grouped_bar": VisualizationType.GROUPED_BAR_CHART,
    "grouped_bar_chart": VisualizationType.GROUPED_BAR_CHART,
    "line": VisualizationType.LINE_CHART,
    "line_chart": VisualizationType.LINE_CHART,
    "trend": VisualizationType.TIME_SERIES,
    "time_series": VisualizationType.TIME_SERIES,
    "timeseries": VisualizationType.TIME_SERIES,
    "network": VisualizationType.NETWORK_GRAPH,
    "network_graph": VisualizationType.NETWORK_GRAPH,
    "scatter": VisualizationType.SCATTER_CHART,
    "scatter_chart": VisualizationType.SCATTER_CHART,
    "scatter_plot": VisualizationType.SCATTER_CHART,
    "histogram": VisualizationType.HISTOGRAM,
    "hist": VisualizationType.HISTOGRAM,
    "distribution": VisualizationType.HISTOGRAM,
}


COUNTRY_ALIASES: dict[str, str] = {
    "argentina": "Argentina",
    "australia": "Australia",
    "austria": "Austria",
    "belgium": "Belgium",
    "brazil": "Brazil",
    "canada": "Canada",
    "china": "China",
    "denmark": "Denmark",
    "france": "France",
    "germany": "Germany",
    "india": "India",
    "ireland": "Ireland",
    "israel": "Israel",
    "italy": "Italy",
    "japan": "Japan",
    "korea": "Korea, Republic of",
    "south_korea": "Korea, Republic of",
    "kr": "Korea, Republic of",
    "mexico": "Mexico",
    "netherlands": "Netherlands",
    "nl": "Netherlands",
    "norway": "Norway",
    "poland": "Poland",
    "spain": "Spain",
    "sweden": "Sweden",
    "switzerland": "Switzerland",
    "taiwan": "Taiwan",
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "great_britain": "United Kingdom",
    "united_kingdom": "United Kingdom",
    "u_k": "United Kingdom",
    "us": "United States",
    "usa": "United States",
    "u_s": "United States",
    "u_s_a": "United States",
    "united_states": "United States",
    "united_states_of_america": "United States",
}


def _enum_values(enum_type: type[StrEnum]) -> str:
    return ", ".join(member.value for member in enum_type)


PUBLIC_TRIAL_PHASE_VALUES = [
    "not_applicable",
    "early_phase_1",
    "phase_1",
    "phase_2",
    "phase_3",
    "phase_4",
]

PUBLIC_STUDY_STATUS_VALUES = [_normalize_key(status.value) for status in StudyStatus]

PUBLIC_VISUALIZATION_TYPE_VALUES = [
    "bar",
    "bar_chart",
    "bar_graph",
    "grouped_bar",
    "grouped_bar_chart",
    "line",
    "line_chart",
    "trend",
    "time_series",
    "timeseries",
    "network",
    "network_graph",
    "scatter",
    "scatter_chart",
    "scatter_plot",
    "histogram",
    "hist",
    "distribution",
]

PUBLIC_COUNTRY_DISPLAY_ALIASES = [
    "GB",
    "KR",
    "NL",
    "UK",
    "US",
    "USA",
]

PUBLIC_COUNTRY_VALUES = sorted(
    set(COUNTRY_ALIASES) | set(COUNTRY_ALIASES.values()) | set(PUBLIC_COUNTRY_DISPLAY_ALIASES)
)


def normalize_trial_phase(value: Any) -> Any:
    if value is None or isinstance(value, TrialPhase):
        return value
    if isinstance(value, str):
        key = _normalize_key(value)
        if key in TRIAL_PHASE_ALIASES:
            return TRIAL_PHASE_ALIASES[key]
    raise ValueError(f"Unsupported trial_phase. Use one of: {_enum_values(TrialPhase)}")


def normalize_study_status(value: Any) -> Any:
    if value is None or isinstance(value, StudyStatus):
        return value
    if isinstance(value, str):
        key = _normalize_key(value)
        if key in STUDY_STATUS_ALIASES:
            return STUDY_STATUS_ALIASES[key]
    raise ValueError(f"Unsupported status. Use one of: {_enum_values(StudyStatus)}")


def normalize_visualization_type(value: Any) -> Any:
    if value is None or isinstance(value, VisualizationType):
        return value
    if isinstance(value, str):
        key = _normalize_key(value)
        if key in VISUALIZATION_TYPE_ALIASES:
            return VISUALIZATION_TYPE_ALIASES[key]
    raise ValueError(
        f"Unsupported visualization type. Use one of: {_enum_values(VisualizationType)}"
    )


def normalize_country(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, str):
        key = _normalize_key(value)
        if key in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[key]
    supported = ", ".join(sorted(set(COUNTRY_ALIASES.values())))
    raise ValueError(f"Unsupported country. Use a supported country name or alias: {supported}")


NormalizedTrialPhase = Annotated[
    TrialPhase,
    BeforeValidator(normalize_trial_phase),
    WithJsonSchema(
        {
            "type": "string",
            "enum": PUBLIC_TRIAL_PHASE_VALUES,
            "description": "Friendly trial phase alias normalized to ClinicalTrials.gov phase.",
        }
    ),
]
NormalizedStudyStatus = Annotated[
    StudyStatus,
    BeforeValidator(normalize_study_status),
    WithJsonSchema(
        {
            "type": "string",
            "enum": PUBLIC_STUDY_STATUS_VALUES,
            "description": "Friendly study status alias normalized to ClinicalTrials.gov status.",
        }
    ),
]
NormalizedCountry = Annotated[
    str,
    BeforeValidator(normalize_country),
    WithJsonSchema(
        {
            "type": "string",
            "enum": PUBLIC_COUNTRY_VALUES,
            "description": "Supported country name or common alias.",
        }
    ),
]
NormalizedVisualizationType = Annotated[
    VisualizationType,
    BeforeValidator(normalize_visualization_type),
    WithJsonSchema(
        {
            "type": "string",
            "enum": PUBLIC_VISUALIZATION_TYPE_VALUES,
            "description": (
                "Friendly visualization type alias normalized to a supported chart type."
            ),
        }
    ),
]
