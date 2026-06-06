import { useState } from "react";
import type { Example, ExampleCategory } from "../types";
import "../styles/components/ExamplesPanel.css";

type Mode = "cache" | "live";

const CATEGORIES: { id: ExampleCategory; label: string }[] = [
  { id: "bar", label: "Bar Charts" },
  { id: "comparison", label: "Comparison" },
  { id: "time", label: "Time Series" },
  { id: "network", label: "Networks" },
  { id: "advanced", label: "Advanced" },
  { id: "system", label: "System" },
];

const CHART_TYPE_COLOR: Record<string, string> = {
  "Bar Chart": "#3b82f6",
  "Bar + Map": "#0ea5e9",
  "Grouped Bar": "#8b5cf6",
  "Line Chart": "#10b981",
  "Time Series": "#f59e0b",
  "Network": "#06b6d4",
  "Scatter": "#f97316",
  "Histogram": "#ef4444",
  "Message": "#6b7280",
};

type Props = {
  examples: Example[];
  selectedId: string;
  onSelect: (example: Example, mode: Mode) => void;
  onModeChange: (mode: Mode) => void;
};

export function ExamplesPanel({ examples, selectedId, onSelect, onModeChange }: Props) {
  const [mode, setMode] = useState<Mode>("cache");
  const [activeCategory, setActiveCategory] = useState<ExampleCategory>("bar");

  function handleModeChange(next: Mode) {
    setMode(next);
    onModeChange(next);
  }

  const filtered = examples.filter((e) => e.category === activeCategory);

  return (
    <section className="examples-panel" aria-label="Example queries">
      <div className="examples-header">
        <span className="examples-title">Examples</span>
        <div className="mode-toggle" role="group" aria-label="Response mode">
          <button
            className={`mode-btn${mode === "cache" ? " active" : ""}`}
            onClick={() => handleModeChange("cache")}
            aria-pressed={mode === "cache"}
          >
            Cache
          </button>
          <button
            className={`mode-btn${mode === "live" ? " active" : ""}`}
            onClick={() => handleModeChange("live")}
            aria-pressed={mode === "live"}
          >
            Live
          </button>
        </div>
      </div>

      {mode === "live" && (
        <p className="mode-hint">
          Click a card to pre-fill the query, then hit <strong>Submit</strong> to fetch live data from ClinicalTrials.gov.
        </p>
      )}

      <div className="category-tabs" role="tablist">
        {CATEGORIES.map((cat) => {
          const count = examples.filter((e) => e.category === cat.id).length;
          return (
            <button
              key={cat.id}
              role="tab"
              aria-selected={activeCategory === cat.id}
              className={`cat-tab${activeCategory === cat.id ? " active" : ""}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.label}
              <span className="cat-count">{count}</span>
            </button>
          );
        })}
      </div>

      <div className="example-cards">
        {filtered.map((example) => (
          <button
            key={example.id}
            className={`example-card${selectedId === example.id ? " selected" : ""}`}
            onClick={() => onSelect(example, mode)}
            title={example.request.query}
          >
            <div className="card-badges">
              <span
                className="badge chart-badge"
                style={{ background: CHART_TYPE_COLOR[example.chartType] ?? "#6b7280" }}
              >
                {example.chartType}
              </span>
              {example.toolCalls > 0 && (
                <span className="badge calls-badge">
                  {example.toolCalls === 1 ? "1 call" : `${example.toolCalls} calls`}
                </span>
              )}
            </div>
            <span className="card-label">{example.label}</span>
            <span className="card-query">{example.request.query}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
