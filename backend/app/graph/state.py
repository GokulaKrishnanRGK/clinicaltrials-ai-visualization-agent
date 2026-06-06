from typing import Any, NotRequired, TypedDict


class GraphState(TypedDict):
    request_id: str
    query: str
    max_records: int
    citation_limit: int
    preferred_visualization: str | None
    drug_name: str | None
    condition: str | None
    trial_phase: str | None
    sponsor: str | None
    country: str | None
    status: str | None
    start_year: int | None
    end_year: int | None

    interpreted: dict[str, Any]
    assumptions: list[str]
    warnings: list[str]

    retrieval_plan: dict[str, Any]
    retrieval_params: dict[str, Any]
    records: list[dict[str, Any]]
    records_retrieved: int
    tool_warnings: list[str]
    repair_count: int

    # Set by assess_data_sufficiency; absent until that node runs.
    records_sufficient: NotRequired[bool]

    agg_type: str | None
    agg_data: Any

    final_response: dict[str, Any] | None
