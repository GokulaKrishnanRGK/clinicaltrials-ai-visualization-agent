import { useCallback, useRef, useState } from "react";

import type { VisualizationApiResponse, VisualizationRequest } from "../types";
import type { NodeState, NodeStatus, StreamEvent } from "./streamTypes";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type StreamStatus = {
  nodes: NodeState[];
  finalResponse: VisualizationApiResponse | null;
  streaming: boolean;
  error: string | null;
};

const INITIAL: StreamStatus = {
  nodes: [],
  finalResponse: null,
  streaming: false,
  error: null,
};

export function useVisualizationStream() {
  const [status, setStatus] = useState<StreamStatus>(INITIAL);
  const abortRef = useRef<AbortController | null>(null);

  const submit = useCallback(async (request: VisualizationRequest) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setStatus({ nodes: [], finalResponse: null, streaming: true, error: null });

    try {
      const res = await fetch(`${BASE_URL}/visualizations/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const event = JSON.parse(raw) as StreamEvent;
            setStatus((prev) => applyEvent(prev, event));
          } catch {
            // ignore malformed events
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setStatus((prev) => ({ ...prev, streaming: false, error: String(err) }));
      return;
    }

    setStatus((prev) => ({ ...prev, streaming: false }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setStatus(INITIAL);
  }, []);

  return { ...status, submit, reset };
}

function applyEvent(prev: StreamStatus, event: StreamEvent): StreamStatus {
  switch (event.type) {
    case "node_start":
      return { ...prev, nodes: upsert(prev.nodes, event.node, { status: "running" }) };

    case "node_retry":
      return {
        ...prev,
        nodes: upsert(prev.nodes, event.node, (n) => ({
          status: "running" as NodeStatus,
          retry_count: event.attempt,
          duration_ms: undefined,
          error: n?.error,
        })),
      };

    case "node_success":
      return {
        ...prev,
        nodes: upsert(prev.nodes, event.node, { status: "success", duration_ms: event.duration_ms }),
      };

    case "node_error":
      return {
        ...prev,
        nodes: upsert(prev.nodes, event.node, { status: "error", error: event.error }),
      };

    case "final_response":
      return { ...prev, finalResponse: event.response };

    default:
      return prev;
  }
}

type Patch =
  | Partial<Omit<NodeState, "name">>
  | ((existing: NodeState | undefined) => Partial<Omit<NodeState, "name">>);

function upsert(nodes: NodeState[], name: string, patch: Patch): NodeState[] {
  const existing = nodes.find((n) => n.name === name);
  const updates = typeof patch === "function" ? patch(existing) : patch;
  if (existing) {
    return nodes.map((n) => (n.name === name ? { ...n, ...updates } : n));
  }
  return [...nodes, { name, status: "pending", retry_count: 0, ...updates }];
}
