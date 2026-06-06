import { useEffect, useMemo, useState } from "react";

import { useGetExamplesQuery } from "./api/clinicalTrialsApi";
import { useVisualizationStream } from "./api/useVisualizationStream";
import { ChartSurface } from "./components/ChartSurface";
import { ControlsPanel } from "./components/ControlsPanel";
import { DashboardHeader } from "./components/DashboardHeader";
import { JsonPanel } from "./components/JsonPanel";
import { MetadataPanel } from "./components/MetadataPanel";
import { NodeTimeline } from "./components/NodeTimeline";
import { responseWithMode } from "./contractUtils";
import { examples as localExamples } from "./data/contractExamples";
import "./styles/app.css";
import type { VisualizationRequest } from "./types";

type Theme = "dark" | "light";

export function App() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [showJson, setShowJson] = useState(false);
  const [selectedId, setSelectedId] = useState(localExamples[0].id);
  const [query, setQuery] = useState(localExamples[0].request.query);
  const [dataMode, setDataMode] = useState<VisualizationRequest["data_mode"]>(
    localExamples[0].request.data_mode,
  );
  const [citationLimit, setCitationLimit] = useState(localExamples[0].request.citation_limit);

  const { data: remoteExamples } = useGetExamplesQuery();
  const stream = useVisualizationStream();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const pickerExamples = remoteExamples ?? localExamples;
  const selectedLocal = localExamples.find((e) => e.id === selectedId) ?? localExamples[0];

  const request = useMemo<VisualizationRequest>(
    () => ({
      ...selectedLocal.request,
      query,
      data_mode: dataMode,
      citation_limit: citationLimit,
    }),
    [citationLimit, dataMode, query, selectedLocal.request],
  );

  const exampleResponse = useMemo(
    () => responseWithMode(selectedLocal.response, dataMode),
    [dataMode, selectedLocal.response],
  );

  const response = stream.finalResponse ?? exampleResponse;
  const showTimeline = stream.streaming || stream.nodes.length > 0;

  const selectExample = (exampleId: string) => {
    const next = localExamples.find((e) => e.id === exampleId) ?? localExamples[0];
    setSelectedId(next.id);
    setQuery(next.request.query);
    setDataMode(next.request.data_mode);
    setCitationLimit(next.request.citation_limit);
    stream.reset();
  };

  return (
    <main className="app-shell">
      <section className="dashboard">
        <DashboardHeader
          response={response}
          theme={theme}
          showJson={showJson}
          onThemeToggle={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
          onJsonToggle={() => setShowJson((v) => !v)}
        />

        <div className="content-grid">
          <div className="left-col">
            <ControlsPanel
              examples={pickerExamples}
              selectedId={selectedId}
              query={query}
              dataMode={dataMode}
              citationLimit={citationLimit}
              isSubmitting={stream.streaming}
              onExampleChange={selectExample}
              onQueryChange={setQuery}
              onDataModeChange={setDataMode}
              onCitationLimitChange={setCitationLimit}
              onSubmit={() => stream.submit(request)}
            />
            {showTimeline && (
              <NodeTimeline
                nodes={stream.nodes}
                streaming={stream.streaming}
                error={stream.error}
              />
            )}
          </div>
          <ChartSurface response={response} citationLimit={citationLimit} />
          <MetadataPanel response={response} />
        </div>

        {showJson && (
          <div className="json-grid">
            <JsonPanel title="Request JSON" value={request} />
            <JsonPanel title="Response JSON" value={response} />
          </div>
        )}
      </section>
    </main>
  );
}
