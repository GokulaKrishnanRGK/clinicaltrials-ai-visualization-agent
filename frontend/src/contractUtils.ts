import type { SourceCitation, VisualizationApiResponse } from "./types";

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
