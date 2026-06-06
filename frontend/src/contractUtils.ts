import type { SourceCitation, VisualizationApiResponse } from "./types";

const _FIELD_LABELS: Record<string, string> = {
  "protocolSection.identificationModule.nctId": "Trial ID",
  "protocolSection.identificationModule.briefTitle": "Brief Title",
  "protocolSection.identificationModule.officialTitle": "Official Title",
  "protocolSection.statusModule.overallStatus": "Overall Status",
  "protocolSection.designModule.phases": "Phase",
  "protocolSection.designModule.studyType": "Study Type",
  "protocolSection.statusModule.startDateStruct.date": "Start Date",
  "protocolSection.conditionsModule.conditions": "Condition",
  "protocolSection.armsInterventionsModule.interventions.name": "Intervention",
  "protocolSection.sponsorCollaboratorsModule.leadSponsor.name": "Lead Sponsor",
  "protocolSection.sponsorCollaboratorsModule.leadSponsor.class": "Sponsor Class",
  "protocolSection.contactsLocationsModule.locations": "Location",
  "protocolSection.contactsLocationsModule.locations.country": "Country",
  interventions: "Intervention",
};

export function formatFieldPath(path: string): string {
  if (_FIELD_LABELS[path]) return _FIELD_LABELS[path];
  const last = path.split(".").pop() ?? path;
  return last.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/^./, (c) => c.toUpperCase());
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
