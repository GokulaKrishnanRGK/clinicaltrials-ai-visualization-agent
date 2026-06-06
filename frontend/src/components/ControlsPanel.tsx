import "../styles/components/ControlsPanel.css";

type ControlsPanelProps = {
  query: string;
  citationLimit: number;
  maxRecords: number;
  isSubmitting: boolean;
  onQueryChange: (query: string) => void;
  onCitationLimitChange: (citationLimit: number) => void;
  onMaxRecordsChange: (maxRecords: number) => void;
  onSubmit: () => void;
};

export function ControlsPanel({
  query,
  citationLimit,
  maxRecords,
  isSubmitting,
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

      <div className="controls-row">
        <div className="field">
          <label htmlFor="citation-limit">Citations</label>
          <input
            id="citation-limit"
            type="number"
            min={0}
            max={25}
            value={citationLimit}
            onChange={(event) => {
              const v = Math.min(25, Math.max(0, Number(event.target.value)));
              onCitationLimitChange(isNaN(v) ? 0 : v);
            }}
          />
        </div>

        <div className="field">
          <label htmlFor="max-records">Records</label>
          <input
            id="max-records"
            type="number"
            min={1}
            max={1000}
            value={maxRecords}
            onChange={(event) => {
              const v = Math.min(1000, Math.max(1, Number(event.target.value)));
              onMaxRecordsChange(isNaN(v) ? 1 : v);
            }}
          />
        </div>
      </div>

      <button className="submit-btn" onClick={onSubmit} disabled={isSubmitting}>
        {isSubmitting ? "Loading…" : "Submit"}
      </button>
    </section>
  );
}
