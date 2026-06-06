import { useState } from "react";

import type { NodeState, NodeStatus } from "../api/streamTypes";
import "../styles/components/NodeTimeline.css";

const NODE_LABELS: Record<string, string> = {
  cache_lookup: "Cache lookup",
  interpret_question: "Interpret",
  plan_tool_calls: "Plan retrieval",
  execute_tool_calls: "Execute tools",
  assess_data_sufficiency: "Assess data",
  repair_plan: "Repair plan",
  aggregate_data: "Aggregate",
  generate_visualization_spec: "Generate spec",
  generate_insight: "Generate insight",
  validate_response: "Validate",
  message_insufficient: "Insufficient data",
};

function StatusIcon({ status }: { status: NodeStatus }) {
  if (status === "running") {
    return (
      <svg className="status-icon spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
        <path d="M12 2a10 10 0 0 1 10 10" />
      </svg>
    );
  }
  if (status === "success") {
    return (
      <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <polyline points="9 12 11 14 15 10" />
      </svg>
    );
  }
  if (status === "retry") {
    return (
      <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M1 4v6h6" />
        <path d="M3.51 15a9 9 0 1 0 .49-4" />
      </svg>
    );
  }
  if (status === "error") {
    return (
      <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="15" y1="9" x2="9" y2="15" />
        <line x1="9" y1="9" x2="15" y2="15" />
      </svg>
    );
  }
  return (
    <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="10" />
    </svg>
  );
}

function ChevronIcon({ expanded }: { expanded: boolean }) {
  return (
    <svg
      className={`chevron-icon${expanded ? " chevron-icon--open" : ""}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

type NodeRowProps = {
  node: NodeState;
  expanded: boolean;
  onToggle: () => void;
};

function NodeRow({ node, expanded, onToggle }: NodeRowProps) {
  const hasSummary = node.status === "success" && !!node.summary;

  return (
    <div className="timeline-item">
      <div
        className={`timeline-row status-${node.status}${hasSummary ? " timeline-row--expandable" : ""}`}
        onClick={hasSummary ? onToggle : undefined}
        role={hasSummary ? "button" : undefined}
        tabIndex={hasSummary ? 0 : undefined}
        onKeyDown={hasSummary ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onToggle(); } } : undefined}
        aria-expanded={hasSummary ? expanded : undefined}
      >
        <StatusIcon status={node.status} />
        <span className="node-label">{NODE_LABELS[node.name] ?? node.name}</span>
        <span className="node-meta">
          {node.duration_ms != null && (
            <span className="node-duration">{node.duration_ms}ms</span>
          )}
          {node.retry_count > 0 && (
            <span className="retry-badge">×{node.retry_count}</span>
          )}
          {hasSummary && <ChevronIcon expanded={expanded} />}
        </span>
      </div>
      {hasSummary && expanded && (
        <div className="node-summary">{node.summary}</div>
      )}
    </div>
  );
}

type NodeTimelineProps = {
  nodes: NodeState[];
  streaming: boolean;
  error: string | null;
};

export function NodeTimeline({ nodes, streaming, error }: NodeTimelineProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const toggle = (name: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  return (
    <section className="node-timeline">
      <h3>{streaming ? "Running…" : "Pipeline"}</h3>
      <div className="timeline-rows">
        {nodes.map((node) => (
          <NodeRow
            key={node.name}
            node={node}
            expanded={expanded.has(node.name)}
            onToggle={() => toggle(node.name)}
          />
        ))}
      </div>
      {error && <p className="timeline-error">{error}</p>}
    </section>
  );
}
