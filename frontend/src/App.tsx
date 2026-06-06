import { useMemo, useState } from "react";

import { useVisualizationStream } from "./api/useVisualizationStream";
import { ControlsPanel } from "./components/ControlsPanel";
import { DashboardHeader } from "./components/DashboardHeader";
import { ExamplesPanel } from "./components/ExamplesPanel";
import { JsonPanel } from "./components/JsonPanel";
import { NodeTimeline } from "./components/NodeTimeline";
import { VisualizationPanel } from "./components/VisualizationPanel";
import { examples as localExamples } from "./data/contractExamples";
import "./styles/app.css";
import type { Example, VisualizationApiResponse, VisualizationRequest } from "./types";

type Theme = "dark" | "light";

export function App() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [showJson, setShowJson] = useState(false);
  const [selectedId, setSelectedId] = useState(localExamples[0].id);
  const [query, setQuery] = useState(localExamples[0].request.query);
  const [previewResponse, setPreviewResponse] = useState<VisualizationApiResponse | null>(null);
  const [isLiveMode, setIsLiveMode] = useState(true);

  const stream = useVisualizationStream();

  const selectedLocal = localExamples.find((e) => e.id === selectedId) ?? localExamples[0];

  const request = useMemo<VisualizationRequest>(
    () => ({
      ...selectedLocal.request,
      query,
    }),
    [query, selectedLocal.request],
  );

  const handleSelectExample = (example: Example, mode: "cache" | "live") => {
    setSelectedId(example.id);
    setQuery(example.request.query);
    stream.reset();
    setPreviewResponse(mode === "cache" ? example.response : null);
  };

  const handleModeChange = (mode: "cache" | "live") => {
    setIsLiveMode(mode === "live");
    if (mode === "live") {
      setPreviewResponse(null);
      stream.reset();
    }
  };

  const handleThemeToggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
  };

  const loading = stream.streaming && stream.finalResponse === null;
  const response = stream.finalResponse ?? previewResponse;

  return (
    <main className="app-shell">
      <section className="dashboard">
        <DashboardHeader
          theme={theme}
          showJson={showJson}
          onThemeToggle={handleThemeToggle}
          onJsonToggle={() => setShowJson((v) => !v)}
        />

        <div className="content-grid">
          <div className="left-col">
            <ControlsPanel
              query={query}
              isSubmitting={stream.streaming}
              onQueryChange={setQuery}
              onSubmit={() => stream.submit(request)}
            />
            {(stream.streaming || stream.nodes.length > 0) && (
              <NodeTimeline
                nodes={stream.nodes}
                streaming={stream.streaming}
                error={stream.error}
              />
            )}
            <ExamplesPanel
              examples={localExamples}
              selectedId={selectedId}
              onSelect={handleSelectExample}
              onModeChange={handleModeChange}
            />
          </div>

          <VisualizationPanel
            response={response}
            loading={loading}
            isLiveMode={isLiveMode}
          />
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
