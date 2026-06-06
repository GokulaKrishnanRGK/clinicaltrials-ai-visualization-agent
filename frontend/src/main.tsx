import React from "react";
import ReactDOM from "react-dom/client";

import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="dashboard">
        <header className="dashboard-header">
          <p className="eyebrow">ClinicalTrials.gov</p>
          <h1>Query-to-Visualization Dashboard</h1>
          <p className="summary">Milestone 1 shell for the clinical-trials analytics dashboard.</p>
        </header>

        <section className="query-panel" aria-label="Query input placeholder">
          <label htmlFor="query">Clinical-trial question</label>
          <textarea
            id="query"
            placeholder="How many Pembrolizumab trials started each year since 2015?"
            disabled
          />
          <button type="button" disabled>
            Generate visualization
          </button>
        </section>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
