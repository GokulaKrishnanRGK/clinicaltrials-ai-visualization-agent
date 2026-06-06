"""
ClinicalTrials.gov API capability summary for LLM prompt injection.

Derives valid enum values directly from the schema enums so the prompt
stays in sync with the code. Call build_capabilities_text() and pass
the result as the `capabilities` variable to the tool_planner prompt.
"""

from __future__ import annotations

from app.schemas.enums import StudyStatus, TrialPhase

# Most common statuses an LLM planner needs to know about, listed first.
_PRIORITY_STATUSES = [
    StudyStatus.RECRUITING,
    StudyStatus.COMPLETED,
    StudyStatus.ACTIVE_NOT_RECRUITING,
    StudyStatus.NOT_YET_RECRUITING,
    StudyStatus.ENROLLING_BY_INVITATION,
    StudyStatus.SUSPENDED,
    StudyStatus.TERMINATED,
    StudyStatus.WITHDRAWN,
]
_RARE_STATUSES = [s for s in StudyStatus if s not in _PRIORITY_STATUSES]


def build_capabilities_text() -> str:
    """Return a compact text block describing CT.gov API capabilities for the planner."""
    priority = " | ".join(s.value for s in _PRIORITY_STATUSES)
    rare = " | ".join(s.value for s in _RARE_STATUSES)
    phases = " | ".join(p.value for p in TrialPhase)

    return f"""\
CLINICALTRIALS.GOV API — SEARCH FIELDS AND CONSTRAINTS

Filter fields and how they map to API parameters:
  condition   → query.cond   Full-text across condition titles and synonyms.
                              Prefer broad MeSH terms for coverage:
                              "Neoplasms" (all cancers) · "Diabetes Mellitus" · "Alzheimer Disease"
                              "Cardiovascular Diseases" · "Depressive Disorder" · "Asthma"
  drug_name   → query.intr   Full-text across intervention/drug names (brand or generic).
  sponsor     → query.spons  Full-text across lead sponsor organization names.
  country     → query.locn   Full-text in facility location text. Use full English country names.
                              This is approximate — it matches city/state text too.
  status      → filter.overallStatus  EXACT enum match (case-sensitive). Use the value as-is.
                Common:  {priority}
                Rare:    {rare}
                !! Use ACTIVE_NOT_RECRUITING — never "ACTIVE" (not a valid API value) !!
  trial_phase → AREA[Phase]  EXACT enum match. Valid values: {phases}
  start_year  → AREA[StartDate] lower bound (integer, inclusive)
  end_year    → AREA[StartDate] upper bound (integer, inclusive)

What the API CANNOT do natively (handled by post-processing after fetch):
  - Sort or rank results by any field
  - Group, count, or aggregate records (by_country / by_phase / by_sponsor all run in memory)
  - Limit to "top N" — fetch up to max_records, aggregation selects the top N after
  - Filter by completion date, enrollment size, or primary outcome
  - OR two different conditions in a single call — use separate labeled calls instead
  - Fetch more than 500 records per call; broad queries are truncated at this limit\
"""
