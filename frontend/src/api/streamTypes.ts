import type { VisualizationApiResponse } from "../types";

export type NodeStatus = "pending" | "running" | "success" | "retry" | "error";

export type NodeState = {
  name: string;
  status: NodeStatus;
  duration_ms?: number;
  retry_count: number;
  error?: string;
  summary?: string;
};

export type NodeStartEvent = { type: "node_start"; node: string };
export type NodeSuccessEvent = { type: "node_success"; node: string; duration_ms: number; summary?: string };
export type NodeErrorEvent = { type: "node_error"; node: string; error: string };
export type NodeRetryEvent = { type: "node_retry"; node: string; attempt: number };
export type FinalResponseEvent = { type: "final_response"; response: VisualizationApiResponse };

export type StreamEvent =
  | NodeStartEvent
  | NodeSuccessEvent
  | NodeErrorEvent
  | NodeRetryEvent
  | FinalResponseEvent;
