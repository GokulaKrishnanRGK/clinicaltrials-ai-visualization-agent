export type VisualizationType =
  | "bar_chart"
  | "grouped_bar_chart"
  | "line_chart"
  | "time_series"
  | "network_graph"
  | "scatter_chart"
  | "histogram";

export type SourceCitation = {
  nct_id: string;
  field: string;
  value: string | number;
  excerpt?: string;
  brief_title?: string;
};

export type ChartDatum = Record<string, string | number | SourceCitation[]>;

export type RenderHints = {
  x_axis_label?: string;
  y_axis_label?: string;
  series_name?: string;
  group_field?: string;
  category_field?: string;
  value_field?: string;
  tooltip_fields?: string[];
  sort?: string;
  legend?: boolean;
};

export type ChartVisualizationSpec = {
  type: Exclude<VisualizationType, "network_graph">;
  title: string;
  description?: string;
  encoding: Record<string, string>;
  data: ChartDatum[];
  render_hints?: RenderHints;
};

export type NetworkNode = {
  id: string;
  label: string;
  type: "drug" | "sponsor" | "condition" | "trial" | "site" | "country";
  value?: number;
  citations: SourceCitation[];
};

export type NetworkEdge = {
  source: string;
  target: string;
  weight: number;
  relation: "sponsors" | "co_occurs_with" | "studies";
  citations: SourceCitation[];
};

export type NetworkVisualizationSpec = {
  type: "network_graph";
  title: string;
  description?: string;
  encoding: Record<string, string>;
  data: {
    nodes: NetworkNode[];
    edges: NetworkEdge[];
  };
  render_hints?: RenderHints;
};

export type VisualizationSpec = ChartVisualizationSpec | NetworkVisualizationSpec;

export type ResponseMetadata = {
  source: "clinicaltrials.gov";
  filters: Record<string, string | number>;
  records_retrieved: number;
  records_used: number;
  generated_at: string;
};

export type VisualizationSuccessResponse = {
  status: "visualization";
  request_id: string;
  visualization: VisualizationSpec;
  meta: ResponseMetadata;
  warnings: string[];
  assumptions: string[];
  insight?: string | null;
};

export type VisualizationMessageResponse = {
  status: "message";
  request_id: string;
  message: string;
  reason:
    | "vague_query"
    | "unsupported_query"
    | "cache_miss"
    | "llm_failure"
    | "api_failure"
    | "insufficient_data"
    | "validation_failure";
  suggested_queries: string[];
  meta: ResponseMetadata | null;
};

export type VisualizationApiResponse = VisualizationSuccessResponse | VisualizationMessageResponse;

export type VisualizationRequest = {
  query: string;
  drug_name?: string;
  condition?: string;
  trial_phase?: string;
  sponsor?: string;
  country?: string;
  status?: string;
  start_year?: number;
  end_year?: number;
  preferred_visualization?: VisualizationType;
};

export type ExampleCategory = "bar" | "comparison" | "time" | "network" | "advanced" | "system";

export type Example = {
  id: string;
  label: string;
  category: ExampleCategory;
  chartType: string;
  toolCalls: number;
  request: VisualizationRequest;
  response: VisualizationApiResponse;
};
