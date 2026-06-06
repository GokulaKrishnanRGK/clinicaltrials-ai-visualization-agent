import ReactECharts from "echarts-for-react";

import { chartOption } from "../charts/options";
import { collectCitations } from "../contractUtils";
import "../styles/components/ChartSurface.css";
import type { VisualizationApiResponse } from "../types";

type ChartSurfaceProps = {
  response: VisualizationApiResponse;
  citationLimit: number;
};

export function ChartSurface({ response, citationLimit }: ChartSurfaceProps) {
  if (response.status === "message") {
    return (
      <section className="chart-empty" aria-live="polite">
        <h2>Message response</h2>
        <p>{response.message}</p>
      </section>
    );
  }

  const citations = collectCitations(response).slice(0, citationLimit);

  return (
    <section className="chart-panel">
      <header className="chart-header">
        <div>
          <h2>{response.visualization.title}</h2>
          {response.visualization.description ? <p>{response.visualization.description}</p> : null}
        </div>
      </header>
      <ReactECharts
        option={chartOption(response.visualization)}
        className={`chart${response.visualization.type === "network_graph" ? " chart--network" : ""}`}
        notMerge
        lazyUpdate
      />
      <section className="citation-list">
        <h3>Citations ({citations.length})</h3>
        {citations.length ? (
          <ul>
            {citations.map((item) => (
              <li key={`${item.nct_id}-${item.field}-${item.value}`} className="citation-item">
                <div className="citation-header">
                  <span className="citation-nct">{item.nct_id}</span>
                  <span className="citation-title">{item.brief_title ?? "Untitled study"}</span>
                </div>
                <div className="citation-meta">
                  <code className="citation-field">{item.field}</code>
                  <span className="citation-value">{String(item.value)}</span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No citations within the current limit.</p>
        )}
      </section>
    </section>
  );
}
