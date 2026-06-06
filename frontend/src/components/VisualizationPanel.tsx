import ReactECharts from "echarts-for-react";

import { chartOption } from "../charts/options";
import { collectCitations } from "../contractUtils";
import "../styles/components/VisualizationPanel.css";
import type { VisualizationApiResponse } from "../types";

type Props = {
  response: VisualizationApiResponse | null;
  citationLimit: number;
  loading?: boolean;
};

export function VisualizationPanel({ response, citationLimit, loading }: Props) {
  if (loading) {
    return (
      <section className="viz-panel viz-panel--loading" aria-busy aria-live="polite">
        <div className="viz-loader" role="status" aria-label="Loading visualization" />
        <span className="viz-loader-label">Fetching data…</span>
      </section>
    );
  }

  if (!response) {
    return (
      <section className="viz-panel viz-panel--empty" aria-live="polite">
        <p>
          Select an example below and click <strong>Submit</strong> to fetch live data from
          ClinicalTrials.gov.
        </p>
      </section>
    );
  }

  if (response.status === "message") {
    return (
      <section className="viz-panel viz-panel--message" aria-live="polite">
        <div className="viz-message-body">
          <h2>{response.reason === "unsupported_query" ? "Out of scope" : "No data found"}</h2>
          <p>{response.message}</p>
          <dl>
            <div>
              <dt>Reason</dt>
              <dd>{response.reason}</dd>
            </div>
            <div>
              <dt>Request ID</dt>
              <dd>{response.request_id}</dd>
            </div>
          </dl>
          {response.suggested_queries.length > 0 && (
            <>
              <h3>Suggested queries</h3>
              <ul>
                {response.suggested_queries.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      </section>
    );
  }

  const { visualization, meta, warnings, assumptions } = response;
  const citations = collectCitations(response).slice(0, citationLimit);
  const isNetwork = visualization.type === "network_graph";

  return (
    <section className="viz-panel">
      <header className="viz-header">
        <h2>{visualization.title}</h2>
        {visualization.description && <p>{visualization.description}</p>}
      </header>

      <ReactECharts
        option={chartOption(visualization)}
        className={`viz-chart${isNetwork ? " viz-chart--network" : ""}`}
        notMerge
        lazyUpdate
      />

      {citationLimit > 0 && (
        <div className="viz-citations">
          <h3>Citations ({citations.length})</h3>
          {citations.length > 0 ? (
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
        </div>
      )}

      <footer className="viz-meta">
        <div className="viz-meta-row">
          <span className="viz-meta-source">{meta.source}</span>
          <span className="viz-meta-sep">·</span>
          <span>
            {meta.records_used} / {meta.records_retrieved} records
          </span>
          <span className="viz-meta-sep">·</span>
          <span>{meta.generated_at.slice(0, 10)}</span>
        </div>
        {warnings.length > 0 && (
          <ul className="viz-notice viz-notice--warning">
            {warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        )}
        {assumptions.length > 0 && (
          <ul className="viz-notice viz-notice--assumption">
            {assumptions.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        )}
      </footer>
    </section>
  );
}
