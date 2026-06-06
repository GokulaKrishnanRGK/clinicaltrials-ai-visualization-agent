import { useMemo, useState } from "react";

import { ChartSurface } from "./components/ChartSurface";
import { ControlsPanel } from "./components/ControlsPanel";
import { DashboardHeader } from "./components/DashboardHeader";
import { JsonPanel } from "./components/JsonPanel";
import { MetadataPanel } from "./components/MetadataPanel";
import { responseWithMode } from "./contractUtils";
import { examples } from "./data/contractExamples";
import "./styles/app.css";
import type { VisualizationRequest } from "./types";

export function App() {
  const [selectedId, setSelectedId] = useState(examples[0].id);
  const selected = examples.find((example) => example.id === selectedId) ?? examples[0];
  const [query, setQuery] = useState(selected.request.query);
  const [dataMode, setDataMode] = useState<VisualizationRequest["data_mode"]>(
    selected.request.data_mode,
  );
  const [citationLimit, setCitationLimit] = useState(selected.request.citation_limit);

  const request = useMemo<VisualizationRequest>(
    () => ({
      ...selected.request,
      query,
      data_mode: dataMode,
      citation_limit: citationLimit,
    }),
    [citationLimit, dataMode, query, selected.request],
  );

  const response = useMemo(
    () => responseWithMode(selected.response, dataMode),
    [dataMode, selected.response],
  );

  const selectExample = (exampleId: string) => {
    const next = examples.find((example) => example.id === exampleId) ?? examples[0];
    setSelectedId(next.id);
    setQuery(next.request.query);
    setDataMode(next.request.data_mode);
    setCitationLimit(next.request.citation_limit);
  };

  return (
    <main className="app-shell">
      <section className="dashboard">
        <DashboardHeader response={response} />

        <ControlsPanel
          examples={examples}
          selectedId={selected.id}
          query={query}
          dataMode={dataMode}
          citationLimit={citationLimit}
          onExampleChange={selectExample}
          onQueryChange={setQuery}
          onDataModeChange={setDataMode}
          onCitationLimitChange={setCitationLimit}
        />

        <div className="main-grid">
          <ChartSurface response={response} citationLimit={citationLimit} />
          <MetadataPanel response={response} />
        </div>

        <div className="json-grid">
          <JsonPanel title="Request JSON" value={request} />
          <JsonPanel title="Response JSON" value={response} />
        </div>
      </section>
    </main>
  );
}
