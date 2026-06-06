import type { VisualizationApiResponse } from "../types";
import "../styles/components/MetadataPanel.css";

type MetadataPanelProps = {
  response: VisualizationApiResponse;
  loading?: boolean;
};

export function MetadataPanel({ response, loading }: MetadataPanelProps) {
  if (loading) {
    return (
      <section className="metadata-panel metadata-panel--loading" aria-busy aria-live="polite">
        <div className="metadata-loader" role="status" aria-label="Loading metadata" />
      </section>
    );
  }

  if (response.status === "message") {
    return (
      <section className="metadata-panel message-panel">
        <h2>Message</h2>
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
        <h3>Suggested queries</h3>
        <ul>
          {response.suggested_queries.map((query) => (
            <li key={query}>{query}</li>
          ))}
        </ul>
      </section>
    );
  }

  const { meta } = response;

  return (
    <section className="metadata-panel">
      <h2>Metadata</h2>
      <dl>
        <div>
          <dt>Records</dt>
          <dd>
            {meta.records_used} used / {meta.records_retrieved} retrieved
          </dd>
        </div>
        <div>
          <dt>Generated</dt>
          <dd>{meta.generated_at}</dd>
        </div>
      </dl>
      <div className="notice-grid">
        <div>
          <h3>Warnings</h3>
          {response.warnings.length ? (
            <ul>
              {response.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p>No warnings.</p>
          )}
        </div>
        <div>
          <h3>Assumptions</h3>
          {response.assumptions.length ? (
            <ul>
              {response.assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          ) : (
            <p>No assumptions.</p>
          )}
        </div>
      </div>
    </section>
  );
}
