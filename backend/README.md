# Clinical Trials Backend

## Local Development

Install dependencies:

```bash
cd backend
uv sync --dev
```

Run the API:

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Format and lint:

```bash
uv run ruff format .
uv run ruff check .
```

## Schema Smoke Check

```bash
uv run python - <<'PY'
from app.schemas import VisualizationRequest

request = VisualizationRequest(
    query="Which countries have the most recruiting Alzheimer's trials?",
    country="USA",
    status="recruiting",
    preferred_visualization="bar",
)

print(request.model_dump(mode="json"))
PY
```

Expected defaults and normalized values:

```json
{
  "query": "Which countries have the most recruiting Alzheimer's trials?",
  "drug_name": null,
  "condition": null,
  "trial_phase": null,
  "sponsor": null,
  "country": "United States",
  "status": "RECRUITING",
  "start_year": null,
  "end_year": null,
  "max_records": 500,
  "preferred_visualization": "bar_chart",
  "data_mode": "cache",
  "citation_limit": 10
}
```
