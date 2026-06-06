import type { VisualizationRequest } from "../types";
import "../styles/components/ControlsPanel.css";

type ExampleOption = { id: string; label: string };

const CITATION_OPTIONS = [0, 3, 5, 10, 15, 20, 25];
const MAX_RECORDS_OPTIONS = [50, 100, 200, 500, 1000];

type ControlsPanelProps = {
  examples: ExampleOption[];
  selectedId: string;
  query: string;
  citationLimit: number;
  maxRecords: number;
  isSubmitting: boolean;
  onExampleChange: (exampleId: string) => void;
  onQueryChange: (query: string) => void;
  onCitationLimitChange: (citationLimit: number) => void;
  onMaxRecordsChange: (maxRecords: number) => void;
  onSubmit: () => void;
};

export function ControlsPanel({
  examples,
  selectedId,
  query,
  citationLimit,
  maxRecords,
  isSubmitting,
  onExampleChange,
  onQueryChange,
  onCitationLimitChange,
  onMaxRecordsChange,
  onSubmit,
}: ControlsPanelProps) {
  return (
    <section className="controls-panel" aria-label="Visualization request controls">
      <div className="field">
        <label htmlFor="query">Clinical-trial question</label>
        <textarea
          id="query"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          rows={4}
        />
      </div>

      <div className="control-row">
        <div className="field">
          <label htmlFor="example">Example response</label>
          <select
            id="example"
            value={selectedId}
            onChange={(event) => onExampleChange(event.target.value)}
          >
            {examples.map((example) => (
              <option value={example.id} key={example.id}>
                {example.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="citation-limit">Citation limit</label>
          <select
            id="citation-limit"
            value={citationLimit}
            onChange={(event) => onCitationLimitChange(Number(event.target.value))}
          >
            {CITATION_OPTIONS.map((n) => (
              <option value={n} key={n}>
                {n === 0 ? "None" : n}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="max-records">Max records</label>
          <select
            id="max-records"
            value={maxRecords}
            onChange={(event) => onMaxRecordsChange(Number(event.target.value))}
          >
            {MAX_RECORDS_OPTIONS.map((n) => (
              <option value={n} key={n}>
                {n}
              </option>
            ))}
          </select>
        </div>

        <button className="submit-btn" onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Loading…" : "Submit"}
        </button>
      </div>
    </section>
  );
}
