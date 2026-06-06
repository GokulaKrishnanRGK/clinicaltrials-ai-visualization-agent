# ClinicalTrials.gov Query-to-Visualization Agent

A backend service and React dashboard that converts natural-language clinical trial questions into structured, source-backed visualization outputs — powered by a LangGraph ReAct agent, ClinicalTrials.gov API v2, and Claude on AWS Bedrock.

---

<!-- SCREENSHOT: Full dashboard screenshot showing a time series chart with the node timeline visible on the left -->
> **Screenshot placeholder** — add a screenshot of the full dashboard here

---

## What it does

You ask a question in plain English:

> *"How has the number of Pembrolizumab trials changed each year since 2015?"*

The agent interprets the query, plans and executes ClinicalTrials.gov API calls, assesses whether the retrieved data is sufficient, aggregates it deterministically in Python, selects a chart type, and returns frontend-ready visualization JSON with per-datum citations to the source trial records.

**Supported visualization types:** time series, bar chart, grouped bar chart (multi-series comparison), scatter plot, histogram, network graph (sponsor–drug and drug co-occurrence).

**Supported query classes:** time trends, category distributions, multi-entity comparisons, geographic rankings, sponsor–drug relationships, drug co-occurrence networks.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          React Dashboard  ·  ECharts  ·  RTK Query           │
│   Query input  ·  Example picker  ·  Node timeline  ·  Map   │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP / SSE  (POST body)
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend                         │
│                                                             │
│  POST /visualizations          POST /visualizations/stream  │
│  POST /visualizations/insight  POST /visualizations/related  │
│  GET  /examples                GET  /health                 │
│                                                             │
│  LangGraph ReAct Agent                                      │
│    interpret_question   →  create_retrieval_plan            │
│    execute_tools        →  assess_data_sufficiency          │
│    repair_plan (≤2x)    →  aggregate_data                   │
│    choose_visualization →  generate_visualization_spec      │
│    validate_response                                        │
│                                                             │
│  Services                                                   │
│    ClinicalTrialsToolInvoker (MCP-ready boundary)           │
│    Prompt registry (versioned YAML)                         │
│    LiteLLM  ·  AWS Bedrock                                  │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
  clinicaltrials.gov/api/v2        AWS Bedrock
  (live or file-based cache)       Claude Sonnet + Haiku
```

### How a query flows through the system

1. `interpret_question` — extracts condition, drug, metric, chart hint, and ambiguity from the natural-language query using Claude Sonnet.
2. `create_retrieval_plan` — decides which tool functions to call, which fields to request, pagination size, and aggregation strategy.
3. `execute_tools` — calls the `ClinicalTrialsToolInvoker` (cache adapter or live API). No LLM involved.
4. `assess_data_sufficiency` — uses Claude Haiku to decide if the records are relevant and complete. If not, routes to repair.
5. `repair_plan` — revises API params and retries. Capped at two repair attempts.
6. `aggregate_data` — counts, groups, ranks, and builds network edges in **pure Python**. The LLM never counts records.
7. `choose_visualization` — selects the best chart type for the aggregation output.
8. `generate_visualization_spec` — builds the final visualization JSON, attaches per-datum citations, and generates an LLM insight and suggested follow-up queries.
9. `validate_response` — enforces the response union schema. One schema-repair call if output is malformed.

---

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- `uv` (Python package manager) — `pip install uv`
- AWS account with Bedrock access and Claude Sonnet 4.6 / Haiku 4.5 enabled in your region

### Backend

```bash
cd backend
uv sync --dev
```

Copy the example environment file and fill in your AWS config:

```bash
cp .env.example .env
```

Start the server:

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","service":"Clinical Trials Query-to-Visualization API"}
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CLINICAL_TRIALS_LLM_MODEL` | `bedrock/global.anthropic.claude-sonnet-4-6` | LiteLLM model string for the primary LLM |
| `AWS_PROFILE` | — | AWS named profile for Bedrock credentials |
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region for Bedrock API calls |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL used by the frontend |

Set `AWS_PROFILE` and `AWS_DEFAULT_REGION` to an account with Bedrock access.

---

## API Reference

### `GET /health`

Returns service status.

```json
{
  "status": "ok",
  "service": "Clinical Trials Query-to-Visualization API"
}
```

---

### `GET /examples`

Returns the canned example queries for the UI picker and manual evaluation.

---

### `POST /visualizations`

**Request body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | `string` | Yes | — | Natural-language clinical trial question |
| `drug_name` | `string` | No | — | Drug or intervention name filter |
| `condition` | `string` | No | — | Condition or disease filter |
| `trial_phase` | `string` | No | — | Phase alias: `phase_1`, `phase_2`, `phase_3`, `phase_4`, `early_phase_1`, `not_applicable` |
| `sponsor` | `string` | No | — | Lead sponsor name filter |
| `country` | `string` | No | — | Country filter. Accepts `US`, `USA`, `United States`, ISO-2 codes |
| `status` | `string` | No | — | Status alias: `recruiting`, `completed`, `active_not_recruiting`, `not_yet_recruiting`, `terminated`, `withdrawn` |
| `start_year` | `integer` | No | — | Filter trials starting on or after this year |
| `end_year` | `integer` | No | — | Filter trials starting on or before this year |
| `preferred_visualization` | `string` | No | — | Chart type hint: `bar_chart`, `grouped_bar_chart`, `line_chart`, `time_series`, `network_graph`, `scatter_chart`, `histogram` |

**Enum normalization:** user-friendly aliases are normalized before API calls. `"bar"` → `"bar_chart"`, `"USA"` → `"United States"`, `"phase 3"` → `"PHASE3"`. Invalid values fail validation with a clear error.

**Example request:**

```json
{
  "query": "How many Pembrolizumab trials started each year since 2015?",
  "drug_name": "Pembrolizumab",
  "start_year": 2015,
  "preferred_visualization": "time_series"
}
```

**Responses:** see [Response Schemas](#response-schemas) below.

---

### `POST /visualizations/stream`

Same request body as `POST /visualizations`. Streams Server-Sent Events (SSE) as the agent graph executes, followed by a `final_response` event.

Use `fetch` with a streaming reader — not `EventSource` — because the request requires a POST body.

**Event types:**

| Event type | Payload fields |
|---|---|
| `node_start` | `node`, `timestamp` |
| `node_success` | `node`, `duration_ms`, `summary` (agent's one-line decision for that node) |
| `node_error` | `node`, `duration_ms`, `error` |
| `node_retry` | `node`, `repair_count` |
| `final_response` | the full `VisualizationApiResponse` union |

The `summary` field in `node_success` exposes the agent's decision at each step — for example: `"assess_data_sufficiency: SUFFICIENT — 312 records, all required fields present"` or `"repair_plan: broadened query, removed phase filter"`.

---

### `POST /visualizations/insight`

Takes a completed `VisualizationSuccessResponse` and returns a 2–3 sentence plain-English observation about the data — generated by Claude Sonnet with the actual data values passed in directly (no hallucination risk).

```json
{ "insight": "Pembrolizumab trial registrations peaked in 2021 with 25 new studies. Activity has declined steadily since, reaching 13 new trials in 2024 — consistent with a maturing indication pipeline following the drug's major FDA approvals in 2019–2021." }
```

---

### `POST /visualizations/related`

Takes a completed `VisualizationSuccessResponse` and returns three contextually relevant follow-up queries that a researcher would naturally ask next.

```json
{ "suggested_followups": [
    "How are Pembrolizumab trials distributed across phases?",
    "Which countries have the most active Pembrolizumab trials?",
    "Show the sponsor network for Pembrolizumab combination studies."
] }
```

---

### Response Schemas

**Visualization success response:**

```json
{
  "status": "visualization",
  "request_id": "req_time_001",
  "visualization": {
    "type": "time_series",
    "title": "Pembrolizumab Trial Starts by Year",
    "description": "Annual new trial registrations for Pembrolizumab since 2015.",
    "encoding": { "x": "year", "y": "trial_count" },
    "data": [
      {
        "year": 2021,
        "trial_count": 25,
        "citations": [
          {
            "nct_id": "NCT05705573",
            "field": "protocolSection.armsInterventionsModule.interventions.name",
            "value": "Pembrolizumab",
            "brief_title": "Adjuvant Pembrolizumab Study"
          }
        ]
      }
    ],
    "render_hints": {
      "x_axis_label": "Start year",
      "y_axis_label": "Trials",
      "series_name": "Trial starts",
      "sort": "chronological"
    }
  },
  "meta": {
    "source": "clinicaltrials.gov",
    "filters": { "drug_name": "Pembrolizumab", "start_year": 2015 },
    "records_retrieved": 126,
    "records_used": 114,
    "generated_at": "2026-06-06T14:32:10Z"
  },
  "warnings": [],
  "assumptions": ["Start year was derived from startDateStruct.date when available."],
  "suggested_followups": [
    "How are Pembrolizumab trials distributed across phases?",
    "Which countries have the most active Pembrolizumab trials?"
  ]
}
```

**Network graph visualization** (`type: "network_graph"`): `data` is `{ nodes: [...], edges: [...] }` instead of a flat array. Nodes have `id`, `label`, `type` (`drug` | `sponsor` | `condition` | `trial` | `site` | `country`), `value`, and `citations`. Edges have `source`, `target`, `weight`, `relation` (`sponsors` | `co_occurs_with` | `studies`), and `citations`.

**Message response** — returned when the query is vague, unsupported, data is insufficient, or an API failure occurs:

```json
{
  "status": "message",
  "request_id": "req_msg_001",
  "message": "This application only answers questions about clinical trials. Please rephrase your question around trial data.",
  "reason": "unsupported_query",
  "suggested_queries": [
    "Show trials for semaglutide by phase",
    "How many Alzheimer's trials are active in the US?"
  ],
  "meta": null
}
```

**`reason` values:** `vague_query`, `unsupported_query`, `llm_failure`, `api_failure`, `insufficient_data`, `validation_failure`.

---

## Example Runs

### 1 — Time series: Pembrolizumab trial starts

**Request:**
```json
{
  "query": "How many Pembrolizumab trials started each year since 2015?",
  "drug_name": "Pembrolizumab",
  "start_year": 2015
}
```

**Response (excerpt):**
```json
{
  "status": "visualization",
  "visualization": {
    "type": "time_series",
    "title": "Pembrolizumab Trial Starts by Year",
    "encoding": { "x": "year", "y": "trial_count" },
    "data": [
      { "year": 2019, "trial_count": 18, "citations": [] },
      { "year": 2020, "trial_count": 21, "citations": [{ "nct_id": "NCT04380636", "field": "protocolSection.statusModule.startDateStruct.date", "value": "2020-05-06", "brief_title": "Pembrolizumab With Chemotherapy" }] },
      { "year": 2021, "trial_count": 25, "citations": [] },
      { "year": 2022, "trial_count": 20, "citations": [] },
      { "year": 2023, "trial_count": 17, "citations": [] },
      { "year": 2024, "trial_count": 13, "citations": [] }
    ]
  },
  "meta": { "source": "clinicaltrials.gov", "records_retrieved": 126, "records_used": 114 },
  "assumptions": ["Start year derived from startDateStruct.date when available."]
}
```

---

### 2 — Grouped bar: Pembrolizumab vs Nivolumab by phase

**Request:**
```json
{
  "query": "Compare Pembrolizumab vs Nivolumab phase distribution.",
  "preferred_visualization": "grouped_bar_chart"
}
```

**Response (excerpt):**
```json
{
  "status": "visualization",
  "visualization": {
    "type": "grouped_bar_chart",
    "title": "Pembrolizumab vs Nivolumab — Trial Phase Distribution",
    "encoding": { "x": "phase", "y": "trial_count", "group": "label" },
    "data": [
      { "phase": "PHASE2", "label": "Pembrolizumab", "trial_count": 134, "citations": [{ "nct_id": "NCT02564263", "field": "protocolSection.designModule.phases", "value": "PHASE2", "brief_title": "Pembrolizumab in Advanced Melanoma" }] },
      { "phase": "PHASE2", "label": "Nivolumab", "trial_count": 109, "citations": [] },
      { "phase": "PHASE3", "label": "Pembrolizumab", "trial_count": 92, "citations": [] },
      { "phase": "PHASE3", "label": "Nivolumab", "trial_count": 78, "citations": [] }
    ],
    "render_hints": { "group_field": "label", "category_field": "phase", "value_field": "trial_count", "legend": true }
  },
  "meta": { "source": "clinicaltrials.gov", "records_retrieved": 573, "records_used": 431 },
  "assumptions": ["Each drug was fetched independently; totals reflect separate API queries.", "Phase NA includes trials with no phase information recorded."]
}
```

---

### 3 — Bar chart + world map: top countries for oncology trials

**Request:**
```json
{
  "query": "Which countries have the most oncology trials? Show the top 20.",
  "condition": "Neoplasms",
  "preferred_visualization": "bar_chart"
}
```

**Response (excerpt):**
```json
{
  "status": "visualization",
  "visualization": {
    "type": "bar_chart",
    "title": "Top 20 Countries by Oncology Trial Count",
    "encoding": { "x": "country", "y": "trial_count" },
    "data": [
      { "country": "United States", "trial_count": 2841, "citations": [{ "nct_id": "NCT04586270", "field": "protocolSection.contactsLocationsModule.locations", "value": "United States", "brief_title": "Lung Cancer Survival Study" }] },
      { "country": "France", "trial_count": 612, "citations": [] },
      { "country": "Germany", "trial_count": 534, "citations": [] }
    ]
  },
  "meta": { "source": "clinicaltrials.gov", "records_retrieved": 6788, "records_used": 6788 },
  "warnings": ["Trials with multiple country sites are counted once per unique country."]
}
```

> The dashboard detects country-axis bar charts and shows a **Map** toggle. The same data is rendered as a world choropleth — no second API call.

---

### 4 — Network graph: GLP-1 drug and condition co-occurrence

**Request:**
```json
{
  "query": "Show how GLP-1 drugs like semaglutide and tirzepatide connect to conditions.",
  "condition": "Obesity",
  "preferred_visualization": "network_graph"
}
```

**Response (excerpt):**
```json
{
  "status": "visualization",
  "visualization": {
    "type": "network_graph",
    "title": "GLP-1 Drug and Condition Co-occurrence Network",
    "data": {
      "nodes": [
        { "id": "sema", "label": "Semaglutide", "type": "drug", "value": 38, "citations": [{ "nct_id": "NCT03548935", "field": "protocolSection.armsInterventionsModule.interventions.name", "value": "Semaglutide", "brief_title": "SUSTAIN-6 Cardiovascular Outcomes" }] },
        { "id": "novo", "label": "Novo Nordisk", "type": "sponsor", "value": 52, "citations": [] }
      ],
      "edges": [
        { "source": "novo", "target": "sema", "weight": 38, "relation": "sponsors", "citations": [] },
        { "source": "sema", "target": "obesity", "weight": 28, "relation": "studies", "citations": [] }
      ]
    }
  },
  "meta": { "source": "clinicaltrials.gov", "records_retrieved": 142, "records_used": 116 }
}
```

---

### 5 — Message response: out-of-scope query

**Request:**
```json
{
  "query": "What is the best recipe for chocolate chip cookies?"
}
```

**Response:**
```json
{
  "status": "message",
  "request_id": "req_msg_001",
  "message": "This application only answers questions about clinical trials — drugs, conditions, trial phases, sponsors, enrollment, and related topics.",
  "reason": "unsupported_query",
  "suggested_queries": [
    "Show trials for semaglutide by phase",
    "How many Alzheimer's trials are active in the US?",
    "Top sponsors for oncology trials"
  ],
  "meta": null
}
```

---

## Design Decisions and Tradeoffs

| Decision | Choice | Rationale |
|---|---|---|
| Agent orchestration | LangGraph | Typed graph state, conditional routing, and repair loops are explicit in code rather than emergent from a prompt chain |
| LLM provider | AWS Bedrock via LiteLLM | No secrets in config files; uses standard AWS credential chain |
| Model split | Sonnet for planning/generation, Haiku for lightweight assessment | Reduces cost on high-frequency assessment calls without sacrificing planning quality |
| Aggregation | Deterministic Python, never LLM | LLMs count unreliably. All grouping, ranking, and network-edge construction runs in `aggregation.py` |
| CT.gov client | MCP-ready tool boundary | The invoker interface, tool functions, and Pydantic contracts are structured so they can be extracted into a FastMCP server without rewriting agent nodes |
| Data mode | Cache default | Enables repeatable demos and evaluation without live API dependency |
| Repair loops | Capped at two | Prevents infinite loops on genuinely sparse queries while giving the agent a real chance to recover from a bad initial plan |
| Schema repair | One call | A single Haiku repair call handles malformed LLM JSON without silently fabricating data |
| Frontend streaming | POST `fetch` reader, not `EventSource` | `EventSource` does not support request bodies; the stream endpoint requires the full visualization request |
| Frontend state | RTK Query + Redux Toolkit | Consistent with idiomatic React data-fetching patterns; RTK Query handles caching and loading states |
| Persistence | Deferred PostgreSQL | No session state needed in this implementation; adds no complexity without sessions |
| Charts | ECharts | Single library covers bar, line, scatter, histogram, and force-directed network graph |

---

## Hallucination Prevention

The agent uses LLMs for reasoning tasks only:

- **Query interpretation** — extracting intent and entities from natural language
- **Retrieval planning** — deciding which API tools and fields to use
- **Data sufficiency assessment** — judging relevance and completeness of retrieved records
- **Repair planning** — revising a failed retrieval plan
- **Visualization selection** — choosing the best chart type
- **Insight generation** — writing a plain-English observation about the final data

The LLM **never** counts records, performs arithmetic, or constructs data points. All of that happens in `backend/app/services/aggregation.py` using standard Python — `defaultdict`, sorted grouping, and explicit edge construction. Pydantic validates every LLM output; a single schema-repair call handles malformed JSON before a message response is returned.

Every number in the visualization output is traceable: each datum includes `citations` with the source `nct_id`, the exact ClinicalTrials.gov JSON field path, and the raw field value that contributed to it.

---

## Limitations

- **Cache mode only covers fixture queries.** Arbitrary queries in cache mode return `reason: "cache_miss"`. Switch to live mode for novel queries.
- **Live mode requires AWS Bedrock access.** Interpreting and planning are LLM-driven; both nodes fall back gracefully if the LLM is unavailable, but the result quality degrades to heuristic-only matching.
- **No session state or follow-up queries.** Each request is independent. Chat-style drill-down requires a separate submission.
- **Network graphs are bounded to top-N nodes.** Very large result sets are pruned before graph construction to keep the visualization readable.
- **ClinicalTrials.gov field coverage is normalized but not exhaustive.** Fields not included in the normalizer are unavailable for aggregation without schema changes.
- **Country name normalization is heuristic.** Minor spelling variations in CT.gov location data may produce split country entries.
- **Results are capped at 100 records per CT.gov API call** (50 per call for multi-call comparison plans). This keeps response latency acceptable (~10s typical) but means broad queries over large disease areas — such as all oncology trials globally — will undersample the full dataset. Aggregation percentages and rankings reflect the sample, not the complete registry.

---

## LLM Cost Model

Each query runs four LLM calls — intent parsing, retrieval planning, visualization spec generation, and insight generation. All four currently use Claude Sonnet 4.6 via AWS Bedrock cross-region inference.

**Prompt caching is already active.** Every system prompt is sent with `cache_control: ephemeral`, so Bedrock caches the static portion of each prompt across requests. Only the human message (user query + variable context) is billed at full input price after the first call.

**Node-level model breakdown (current vs. optimised):**

| Node | Task complexity | Current | Optimised |
|---|---|---|---|
| `interpret_question` | Structured NLP extraction | Sonnet 4.6 | Haiku 4.5 |
| `create_retrieval_plan` | Multi-step routing with few-shot examples | Sonnet 4.6 | Sonnet 4.6 (keep) |
| `generate_visualization_spec` | Agg-type → encoding lookup | Sonnet 4.6 | Haiku 4.5 |
| `generate_insight` | Short text generation from data points | Sonnet 4.6 | Haiku 4.5 |

`create_retrieval_plan` stays on Sonnet because it must reason over 12 aggregation types, 9 few-shot examples, and multi-call comparison plans — this is where query-routing errors are most costly.

**Per-query cost estimate (approximate, based on Anthropic API list prices):**

| Scenario | Input tokens | Output tokens | Cost/query |
|---|---|---|---|
| All Sonnet, no caching | ~2,900 | ~500 | ~$0.016 |
| All Sonnet, with caching *(current)* | ~1,100 uncached + 1,820 cache read | ~500 | ~$0.011 |
| Haiku for 3 nodes + Sonnet for planner, with caching | ~600 Haiku + 500 Sonnet uncached | ~500 | ~$0.007 |

Token breakdown: ~1,820 tokens are system prompts (cacheable); ~1,100 tokens are per-query human messages (capabilities string, user query, variable context). Output is ~500 tokens across all four calls.

**Estimated cost for 10,000 queries:**

| Scenario | Cost |
|---|---|
| All Sonnet, no caching | ~$160 |
| All Sonnet, with caching *(current)* | ~$110 |
| Mixed Haiku/Sonnet, with caching *(future)* | ~$70 |

Prompt caching alone saves ~31% vs uncached. Routing the three simpler nodes to Haiku saves an additional ~36%, reaching ~56% total reduction vs the uncached baseline.

> These are estimates based on Anthropic API list prices. AWS Bedrock cross-region inference pricing is comparable but may differ by ±10–20%. Actual costs vary with query length and data volume passed to the insight node.

---

## Future Work

- **Sessions and chat follow-up** — maintain query context across turns; support drill-down without re-running the full retrieval plan.
- **PostgreSQL** — durable storage for visualization runs, session history, and cached API responses.
- **Qdrant vector store** — semantic retrieval over cached trial records using Amazon Titan Embed Text v2, reducing live API dependency for common query patterns.
- **FastMCP extraction** — the CT.gov tool boundary is already structured for this; extracting it behind FastMCP transport is a configuration change, not a rewrite.
- **Alternative visualization switcher** — return multiple valid chart types for the same aggregation output so the user can switch rendering without re-querying.
- **Structured filter controls in the UI** — the request schema already supports all filters; the frontend currently exposes only the query and citation limit.
- **Haiku routing for simple nodes** — route `interpret_question`, `generate_visualization_spec`, and `generate_insight` to Claude Haiku 4.5. The prompt registry already supports per-prompt `model_preference`; this is a one-line change per prompt file. See the cost model above for projected savings.
- **LLM observability with Langfuse** — instrument every LLM call (intent interpretation, retrieval planning) with Langfuse traces, capturing inputs, outputs, latency, token usage, and model version per request. Langfuse datasets would store the eval cases alongside human-annotated expected outputs, enabling dataset-driven regression runs directly from the Langfuse UI.
- **Human-annotated evaluation datasets** — collect ground-truth labels from domain experts (correct chart type, expected aggregation keys, acceptable citation sources) and store them as versioned datasets in Langfuse for reproducible benchmark runs across prompt and model changes.
- **RAGAS and LLM-as-judge scoring** — augment the deterministic eval harness with RAGAS metrics (faithfulness, answer relevance, context precision) for retrieval quality, and an LLM-as-judge layer that scores whether the chosen visualization correctly answers the user's question and whether warnings are appropriate.
- **Docker Compose** — convenience wrapper for local development; the current target is direct local execution.
- **Multi-user cloud deployment** — see architecture below.

### Cloud Architecture for Multi-User Scale

The current design is stateless and horizontally scalable. The main change for production is decoupling request acceptance from pipeline execution via a queue, so the 10–15s LangGraph pipeline doesn't block the API tier under concurrent load.

```
User browser
      │  HTTPS
      ▼
[CloudFront + S3]                    ← React SPA served from edge
      │  /api/*
      ▼
[Application Load Balancer]
      │
      ├──► [ECS Fargate — FastAPI]        ← stateless API layer (auto-scaled)
      │         │  POST /visualizations
      │         │  enqueue job → return job_id
      │         ▼
      │    [SQS Queue]                    ← decouples acceptance from pipeline execution
      │         │
      │         ▼
      │    [ECS Fargate — LangGraph Workers]   ← pipeline execution (auto-scaled)
      │         │  one worker per query
      │         ├──► [AWS Bedrock]             ← Claude Sonnet — intent + planning
      │         ├──► [ClinicalTrials.gov API]  ← live trial data retrieval
      │         ├──► [Qdrant Cloud]            ← semantic cache / trial record index
      │         └──► [Aurora PostgreSQL]       ← write completed response + session
      │
      ├──► [Aurora PostgreSQL Multi-AZ]        ← sessions, cached responses, audit log
      └──► [Qdrant Cloud]                      ← trial record embeddings
                    │
                    └──► [AWS Bedrock]
                           Titan Embed Text v2 — dense embeddings
```

**Key scaling decisions:**

- **Stateless API tier** — FastAPI containers hold no state; ALB can route any request to any instance. Scales horizontally on CPU/request-count metrics.
- **SQS decoupling** — the API returns a `job_id` immediately; the 10–15s pipeline runs asynchronously. Clients poll `GET /visualizations/{job_id}` or connect via WebSocket for push delivery.
- **Worker autoscaling** — ECS scales the LangGraph worker fleet on SQS queue depth. Burst traffic queues rather than dropping requests.
- **Bedrock provisioned throughput** — on-demand Bedrock is sufficient at low concurrency; provisioned throughput removes per-request latency variance under sustained load.
- **Qdrant semantic cache** — embeds past queries and retrieves near-duplicate responses without re-running the LLM pipeline, cutting cost and latency for repeated or similar queries.
- **Aurora Multi-AZ** — read replicas serve session history and cached responses; the writer handles inserts only.

---

## AI Tools and Validation

**Tools used:** Claude Code (Anthropic) and OpenAI Codex were used throughout the development workflow. Development was structured as a multi-agent workflow using git worktrees to parallelize independent workstreams — for example, running frontend and backend feature branches concurrently without context-switching overhead.

All architectural decisions were made by me through spec-driven development: the system design, data contracts, agent topology, and tradeoffs were fully specced in `docs/SPEC.md` and `docs/MILESTONES.md` before any implementation began. The AI coding agents were used for the actual application development workflows — translating those decisions into working code — not for making architectural choices.

**What was deliberate vs generated:**

- Deliberate: the ReAct agent topology, the decision to never let the LLM aggregate data, the MCP-ready service boundary, the response union schema, the citation-per-datum design, the prompt registry design.
- Generated and adapted: FastAPI router scaffolding, Pydantic model boilerplate, ECharts option builders, RTK Query slice setup.

**How correctness was validated:**

- **Evaluation harness:** `eval/run_eval.py` runs 18 cases covering all example query types — bar charts, grouped bars, time series, scatter, histogram, network graphs, and message responses — through the live `POST /visualizations` endpoint with deterministic validators. Last run: **18/18 pass**, average latency 10.6s. Run with:

  ```bash
  cd backend
  AWS_PROFILE=<bedrock-profile> uv run python eval/run_eval.py
  ```

- Schema validation was smoke-tested with invalid enum values and missing required fields.
- Aggregation functions were verified by inspection against known fixture record counts.
- Live mode was spot-checked against direct ClinicalTrials.gov API responses to confirm normalization accuracy.
- The repair loop was triggered by deliberately narrow queries and observed to broaden correctly on the second attempt.
- Running the eval harness surfaced and fixed three latent bugs: `scatter_chart` and `histogram` missing from the `ChartVisualizationSpec.type` Literal (HTTP 500), and three agg types missing from the `visualize.py` dispatch table.
