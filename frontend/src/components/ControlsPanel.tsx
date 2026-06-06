import "../styles/components/ControlsPanel.css";

type ControlsPanelProps = {
  query: string;
  isSubmitting: boolean;
  onQueryChange: (query: string) => void;
  onSubmit: () => void;
};

export function ControlsPanel({
  query,
  isSubmitting,
  onQueryChange,
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

      <button className="submit-btn" onClick={onSubmit} disabled={isSubmitting}>
        {isSubmitting ? "Loading…" : "Submit"}
      </button>
    </section>
  );
}
