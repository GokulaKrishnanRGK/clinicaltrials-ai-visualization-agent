import { useEffect, useMemo, useState } from "react";

import { useGetExamplesQuery } from "./store/clinicalTrialsApi";
import { useVisualizationStream } from "./api/useVisualizationStream";
import { ChartSurface } from "./components/ChartSurface";
import { ControlsPanel } from "./components/ControlsPanel";
import { DashboardHeader } from "./components/DashboardHeader";
import { JsonPanel } from "./components/JsonPanel";
import { MetadataPanel } from "./components/MetadataPanel";
import { NodeTimeline } from "./components/NodeTimeline";
import { examples as localExamples } from "./data/contractExamples";
import "./styles/app.css";
import type { VisualizationRequest } from "./types";

type Theme = "dark" | "light";

export function App() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [showJson, setShowJson] = useState(false);
  const [selectedId, setSelectedId] = useState(localExamples[0].id);
  const [query, setQuery] = useState(localExamples[0].request.query);
  const [citationLimit, setCitationLimit] = useState(localExamples[0].request.citation_limit);
  const [maxRecords, setMaxRecords] = useState(localExamples[0].request.max_records);

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
      citation_limit: citationLimit,
      max_records: maxRecords,
    }),
    [citationLimit, maxRecords, query, selectedLocal.request],
  );

  const exampleResponse = selectedLocal.response;

  const loading = stream.streaming && stream.finalResponse === null;
  const response = stream.finalResponse ?? exampleResponse;
  const showTimeline = stream.streaming || stream.nodes.length > 0;

  const selectExample = (exampleId: string) => {
    const next = localExamples.find((e) => e.id === exampleId) ?? localExamples[0];
    setSelectedId(next.id);
    setQuery(next.request.query);
    setCitationLimit(next.request.citation_limit);
    setMaxRecords(next.request.max_records);
    stream.reset();
  };

  return (
    <main className="app-shell">
      <section className="dashboard">
        <DashboardHeader
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
              citationLimit={citationLimit}
              maxRecords={maxRecords}
              isSubmitting={stream.streaming}
              onExampleChange={selectExample}
              onQueryChange={setQuery}
              onCitationLimitChange={setCitationLimit}
              onMaxRecordsChange={setMaxRecords}
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
          <ChartSurface response={response} citationLimit={citationLimit} loading={loading} />
          <MetadataPanel response={response} loading={loading} />
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
