import { useEffect } from "react";

import "../styles/components/CitationPanel.css";
import { formatFieldPath } from "../contractUtils";
import type { SourceCitation } from "../types";

type Props = {
  label: string;
  citations: SourceCitation[];
  citationLimit: number;
  onClose: () => void;
};

export function CitationPanel({ label, citations, citationLimit, onClose }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  const empty = citationLimit === 0 || citations.length === 0;

  return (
    <>
      <div className="cp-overlay" onClick={onClose} aria-hidden />
      <aside className="cp-panel" role="dialog" aria-modal aria-label={`Citations for ${label}`}>
        <header className="cp-header">
          <div className="cp-title">
            <span className="cp-eyebrow">Citations</span>
            <h3>{label}</h3>
          </div>
          <button className="cp-close" onClick={onClose} aria-label="Close citations">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </header>
        <div className="cp-body">
          {empty ? (
            <p className="cp-empty">No citations available for this data point.</p>
          ) : (
            <ul className="cp-list">
              {citations.map((c) => (
                <li key={`${c.nct_id}-${c.field}`} className="cp-item">
                  <div className="cp-nct-row">
                    <a
                      href={`https://clinicaltrials.gov/study/${c.nct_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="cp-nct"
                    >
                      {c.nct_id}
                    </a>
                    {c.brief_title && <span className="cp-brief">{c.brief_title}</span>}
                  </div>
                  <div className="cp-meta">
                    <span className="cp-field">{formatFieldPath(c.field)}</span>
                    <span className="cp-value">{String(c.value)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>
    </>
  );
}
