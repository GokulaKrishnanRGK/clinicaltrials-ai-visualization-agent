import type { VisualizationApiResponse } from "../types";
import "../styles/components/DashboardHeader.css";

type DashboardHeaderProps = {
  response: VisualizationApiResponse;
  theme: "dark" | "light";
  showJson: boolean;
  onThemeToggle: () => void;
  onJsonToggle: () => void;
};

function SunIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="4" />
      <line x1="12" y1="2" x2="12" y2="5" />
      <line x1="12" y1="19" x2="12" y2="22" />
      <line x1="5.64" y1="5.64" x2="7.76" y2="7.76" />
      <line x1="16.24" y1="16.24" x2="18.36" y2="18.36" />
      <line x1="2" y1="12" x2="5" y2="12" />
      <line x1="19" y1="12" x2="22" y2="12" />
      <line x1="5.64" y1="18.36" x2="7.76" y2="16.24" />
      <line x1="16.24" y1="7.76" x2="18.36" y2="5.64" />
    </svg>
  );
}

function MoonIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function BracesIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1" />
      <path d="M16 3h1a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0-2 2v5a2 2 0 0 1-2 2h-1" />
    </svg>
  );
}

export function DashboardHeader({
  response,
  theme,
  showJson,
  onThemeToggle,
  onJsonToggle,
}: DashboardHeaderProps) {
  return (
    <header className="dashboard-header">
      <h1>Clinical Trials Dashboard</h1>
      <div className="header-right">
        <div className="header-metrics" aria-label="Current response summary">
          <span>{response.status}</span>
          <span>
            {response.status === "visualization" ? response.visualization.type : response.reason}
          </span>
        </div>

        <button
          className="json-toggle"
          aria-pressed={showJson}
          onClick={onJsonToggle}
          title={showJson ? "Hide JSON panels" : "Show JSON panels"}
        >
          <BracesIcon />
          JSON
        </button>

        <button
          className="theme-slider"
          role="switch"
          aria-checked={theme === "dark"}
          onClick={onThemeToggle}
          aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
        >
          <SunIcon className={`theme-icon${theme === "light" ? " active" : ""}`} />
          <span className="slider-track">
            <span className={`slider-thumb${theme === "dark" ? " is-dark" : ""}`} />
          </span>
          <MoonIcon className={`theme-icon${theme === "dark" ? " active" : ""}`} />
        </button>
      </div>
    </header>
  );
}
