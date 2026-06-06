import type { Example, VisualizationRequest } from "../types";
import "../styles/components/ControlsPanel.css";

type ControlsPanelProps = {
  examples: Example[];
  selectedId: string;
  query: string;
  dataMode: VisualizationRequest["data_mode"];
  citationLimit: number;
  onExampleChange: (exampleId: string) => void;
  onQueryChange: (query: string) => void;
  onDataModeChange: (dataMode: VisualizationRequest["data_mode"]) => void;
  onCitationLimitChange: (citationLimit: number) => void;
};

export function ControlsPanel({
  examples,
  selectedId,
  query,
  dataMode,
  citationLimit,
  onExampleChange,
  onQueryChange,
  onDataModeChange,
  onCitationLimitChange,
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

        <fieldset className="segmented-control">
          <legend>Data mode</legend>
          <label>
            <input
              type="radio"
              name="data-mode"
              checked={dataMode === "cache"}
              onChange={() => onDataModeChange("cache")}
            />
            Cache
          </label>
          <label>
            <input
              type="radio"
              name="data-mode"
              checked={dataMode === "live"}
              onChange={() => onDataModeChange("live")}
            />
            Live
          </label>
        </fieldset>

        <div className="field citation-control">
          <label htmlFor="citation-limit">Citation limit</label>
          <input
            id="citation-limit"
            type="range"
            min="0"
            max="25"
            value={citationLimit}
            onChange={(event) => onCitationLimitChange(Number(event.target.value))}
          />
          <output htmlFor="citation-limit">{citationLimit}</output>
        </div>
      </div>
    </section>
  );
}
