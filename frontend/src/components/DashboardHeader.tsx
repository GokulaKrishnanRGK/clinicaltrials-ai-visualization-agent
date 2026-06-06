import type { VisualizationApiResponse } from "../types";
import "../styles/components/DashboardHeader.css";

type DashboardHeaderProps = {
  response: VisualizationApiResponse;
};

export function DashboardHeader({ response }: DashboardHeaderProps) {
  return (
    <header className="dashboard-header">
      <div>
        <p className="eyebrow">Milestone 9</p>
        <h1>Clinical Trials Contract Dashboard</h1>
      </div>
      <div className="header-metrics" aria-label="Current response summary">
        <span>{response.status}</span>
        <span>
          {response.status === "visualization" ? response.visualization.type : response.reason}
        </span>
      </div>
    </header>
  );
}
