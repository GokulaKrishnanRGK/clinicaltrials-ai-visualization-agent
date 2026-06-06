import type { SourceCitation, VisualizationApiResponse, VisualizationRequest } from "./types";

export function responseWithMode(
  response: VisualizationApiResponse,
  dataMode: VisualizationRequest["data_mode"],
): VisualizationApiResponse {
  if (!response.meta) {
    return response;
  }

  return {
    ...response,
    meta: {
      ...response.meta,
      data_mode: dataMode,
    },
  };
}

export function collectCitations(response: VisualizationApiResponse): SourceCitation[] {
  if (response.status !== "visualization") {
    return [];
  }

  if (response.visualization.type === "network_graph") {
    return [
      ...response.visualization.data.nodes.flatMap((node) => node.citations),
      ...response.visualization.data.edges.flatMap((edge) => edge.citations),
    ];
  }

  return response.visualization.data.flatMap((datum) => {
    const citations = datum.citations;
    return Array.isArray(citations) ? (citations as SourceCitation[]) : [];
  });
}
