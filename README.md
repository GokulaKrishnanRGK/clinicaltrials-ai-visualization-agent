# Clinical Trials Query-to-Visualization Agent

Backend-first ClinicalTrials.gov query-to-visualization application with a React dashboard.

## Local Development

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ruff:

```bash
cd backend
uv run ruff format .
uv run ruff check .
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>.

Prettier:

```bash
cd frontend
npm run format:check
```

## API Schema Examples

### Visualization Request

```json
{
  "query": "Which countries have the most recruiting Alzheimer's trials?",
  "country": "USA",
  "status": "recruiting",
  "preferred_visualization": "bar",
  "data_mode": "cache",
  "max_records": 500,
  "citation_limit": 10
}
```

The backend normalizes friendly aliases before tool execution. For example, `USA`
becomes `United States`, `phase 3` becomes `PHASE3`, and `bar` becomes
`bar_chart`. Unknown enum or alias values fail request validation.

### Visualization Response

```json
{
  "status": "visualization",
  "request_id": "req_123",
  "visualization": {
    "type": "time_series",
    "title": "Trials per year",
    "encoding": {
      "x": "year",
      "y": "trial_count"
    },
    "data": [
      {
        "year": 2024,
        "trial_count": 3,
        "citations": [
          {
            "nct_id": "NCT00000001",
            "field": "protocolSection.statusModule.startDateStruct.date",
            "value": "2024-01-01",
            "brief_title": "Example study"
          }
        ]
      }
    ],
    "render_hints": {
      "x_axis_label": "Year",
      "y_axis_label": "Trials"
    }
  },
  "meta": {
    "source": "clinicaltrials.gov",
    "data_mode": "cache",
    "filters": {
      "country": "United States"
    },
    "records_retrieved": 3,
    "records_used": 3,
    "generated_at": "2026-06-06T00:00:00Z"
  },
  "warnings": [],
  "assumptions": []
}
```

### Message Response

```json
{
  "status": "message",
  "request_id": "req_124",
  "message": "This query is not available in cache mode. Switch to live mode or choose a canned example.",
  "reason": "cache_miss",
  "suggested_queries": [
    "How many Pembrolizumab trials started each year since 2015?"
  ],
  "meta": null
}
```
