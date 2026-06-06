import ReactECharts from "echarts-for-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { chartOption, choroplethOption } from "../charts/options";
import { ensureWorldMap, isWorldMapRegistered, COUNTRY_ALIASES } from "../charts/worldMap";
import { collectCitations } from "../contractUtils";
import "../styles/components/VisualizationPanel.css";
import type {
  ChartDatum,
  ChartVisualizationSpec,
  SourceCitation,
  VisualizationApiResponse,
  VisualizationSpec,
} from "../types";
import { CitationPanel } from "./CitationPanel";

type ViewMode = "bar" | "map";
type MapState = "idle" | "loading" | "ready" | "error";

type PanelState = { label: string; citations: SourceCitation[] };

function isCountryBarChart(viz: VisualizationSpec): viz is ChartVisualizationSpec {
  return viz.type === "bar_chart" && viz.encoding.x === "country";
}

type Props = {
  response: VisualizationApiResponse | null;
  citationLimit: number;
  loading?: boolean;
};

export function VisualizationPanel({ response, citationLimit, loading }: Props) {
  const [viewMode, setViewMode] = useState<ViewMode>("bar");
  const [mapState, setMapState] = useState<MapState>(
    isWorldMapRegistered() ? "ready" : "idle",
  );
  const [citationPanel, setCitationPanel] = useState<PanelState | null>(null);

  // Reset view state whenever the response changes
  useEffect(() => {
    setViewMode("bar");
    setCitationPanel(null);
  }, [response]);

  const handleMapToggle = async () => {
    setViewMode("map");
    if (mapState === "idle" || mapState === "error") {
      setMapState("loading");
      const ok = await ensureWorldMap();
      setMapState(ok ? "ready" : "error");
    }
  };

  const handleChartClick = useCallback(
    (params: unknown) => {
      if (!response || response.status !== "visualization") return;
      const viz = response.visualization;

      const p = params as {
        componentType?: string;
        name?: string;
        seriesName?: string;
        dataIndex?: number;
        dataType?: string;
        data?: unknown;
      };

      if (p.componentType !== "series") return;

      // ── Network graph ──────────────────────────────────────────────────
      if (viz.type === "network_graph") {
        if (p.dataType === "node") {
          const nodeData = p.data as { id: string };
          const node = viz.data.nodes.find((n) => n.id === nodeData.id);
          if (node) setCitationPanel({ label: node.label, citations: node.citations });
        } else if (p.dataType === "edge") {
          const edgeData = p.data as { source: string; target: string };
          const edge = viz.data.edges.find(
            (e) => e.source === edgeData.source && e.target === edgeData.target,
          );
          if (edge) {
            setCitationPanel({
              label: `${edgeData.source} → ${edgeData.target}`,
              citations: edge.citations,
            });
          }
        }
        return;
      }

      // ── Chart types ────────────────────────────────────────────────────
      const { x, group } = viz.encoding;
      const hints = viz.render_hints;

      function extractCitations(datum: ChartDatum): SourceCitation[] {
        const raw = datum.citations;
        return Array.isArray(raw) ? (raw as SourceCitation[]) : [];
      }

      if (viz.type === "scatter_chart") {
        const idx = p.dataIndex;
        if (idx !== undefined && idx >= 0 && idx < viz.data.length) {
          const datum = viz.data[idx];
          setCitationPanel({ label: `Point ${idx + 1}`, citations: extractCitations(datum) });
        }
        return;
      }

      if (viz.type === "grouped_bar_chart") {
        const catField = hints?.category_field ?? x;
        const grpField = hints?.group_field ?? group ?? "";
        const datum = viz.data.find(
          (d) => String(d[catField]) === p.name && String(d[grpField]) === p.seriesName,
        );
        if (datum) {
          setCitationPanel({
            label: `${p.name ?? ""} · ${p.seriesName ?? ""}`,
            citations: extractCitations(datum),
          });
        }
        return;
      }

      // bar_chart, line_chart, time_series, histogram — and choropleth map view
      let datum: ChartDatum | undefined;
      if (viewMode === "map") {
        datum = viz.data.find((d) => {
          const raw = String(d[x]);
          return (COUNTRY_ALIASES[raw] ?? raw) === p.name || raw === p.name;
        });
      } else {
        datum = viz.data.find((d) => String(d[x]) === p.name);
      }
      if (datum) {
        setCitationPanel({ label: String(p.name ?? ""), citations: extractCitations(datum) });
      }
    },
    [response, viewMode],
  );

  const onEvents = useMemo(() => ({ click: handleChartClick }), [handleChartClick]);

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
  const showMapToggle = isCountryBarChart(visualization);

  const chartOpt =
    showMapToggle && viewMode === "map" && mapState === "ready"
      ? choroplethOption(visualization as ChartVisualizationSpec)
      : chartOption(visualization);

  return (
    <section className="viz-panel">
      <header className="viz-header">
        <div className="viz-header-text">
          <h2>{visualization.title}</h2>
          {visualization.description && <p>{visualization.description}</p>}
        </div>

        {showMapToggle && (
          <div className="chart-view-toggle" role="group" aria-label="Chart view">
            <button
              className={`view-btn${viewMode === "bar" ? " active" : ""}`}
              onClick={() => setViewMode("bar")}
            >
              Bar
            </button>
            <button
              className={`view-btn${viewMode === "map" ? " active" : ""}`}
              onClick={handleMapToggle}
              disabled={mapState === "loading"}
            >
              {mapState === "loading" ? "…" : "Map"}
            </button>
          </div>
        )}
      </header>

      {viewMode === "map" && mapState === "loading" && (
        <div className="viz-map-loading">
          <div className="viz-loader" />
          <span className="viz-loader-label">Loading world map…</span>
        </div>
      )}

      {viewMode === "map" && mapState === "error" && (
        <div className="viz-map-error">
          <p>Could not load world map — check your network connection.</p>
          <button onClick={handleMapToggle}>Retry</button>
        </div>
      )}

      {(viewMode === "bar" || (viewMode === "map" && mapState === "ready")) && (
        <ReactECharts
          option={chartOpt}
          className={`viz-chart${isNetwork ? " viz-chart--network" : ""}${viewMode === "map" ? " viz-chart--map" : ""}`}
          notMerge
          lazyUpdate
          onEvents={onEvents}
        />
      )}

      {response.insight && (
        <div className="viz-insight">
          <span className="viz-insight-label">What this data shows</span>
          <p>{response.insight}</p>
        </div>
      )}

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

      {citationPanel !== null && (
        <CitationPanel
          label={citationPanel.label}
          citations={citationPanel.citations}
          citationLimit={citationLimit}
          onClose={() => setCitationPanel(null)}
        />
      )}
    </section>
  );
}
