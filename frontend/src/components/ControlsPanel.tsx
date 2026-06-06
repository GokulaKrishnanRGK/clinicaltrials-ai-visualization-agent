import type { VisualizationRequest } from "../types";
import "../styles/components/ControlsPanel.css";

type ExampleOption = { id: string; label: string };

const CITATION_OPTIONS = [0, 3, 5, 10, 25];

type ControlsPanelProps = {
  examples: ExampleOption[];
  selectedId: string;
  query: string;
  citationLimit: number;
  isSubmitting: boolean;
  onExampleChange: (exampleId: string) => void;
  onQueryChange: (query: string) => void;
  onCitationLimitChange: (citationLimit: number) => void;
  onSubmit: () => void;
};

export function ControlsPanel({
  examples,
  selectedId,
  query,
  citationLimit,
  isSubmitting,
  onExampleChange,
  onQueryChange,
  onCitationLimitChange,
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

        <button className="submit-btn" onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Loading…" : "Submit"}
        </button>
      </div>
    </section>
  );
}
