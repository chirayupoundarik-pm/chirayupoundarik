# chirayupoundarik
Building AI Products to solve observability problems

---

## Email Drafting Agent

A lightweight Python agent that uses OpenAI's API to **analyze incoming emails** and **generate contextual draft responses** automatically.

### Features

- **Email analysis** — extracts intent, tone, urgency, key points, and required actions from any email.
- **Draft generation** — writes a professional, context-aware reply that addresses every key point.
- **Full pipeline** — a single `process_email()` call runs both steps and returns structured output.
- **Configurable** — pass your name, the sender's name, and any additional instructions to shape the reply.

---

### Project Structure

```
.
├── email_agent.py   # Main agent: analyze_email(), generate_draft_response(), process_email()
├── requirements.txt # Python dependencies
└── README.md
```

---

### Setup

#### 1. Clone the repository

```bash
git clone <repo-url>
cd chirayupoundarik
```

#### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."   # macOS / Linux
set OPENAI_API_KEY=sk-...        # Windows CMD
$env:OPENAI_API_KEY="sk-..."     # Windows PowerShell
```

You can obtain an API key from [platform.openai.com](https://platform.openai.com/api-keys).

---

### Usage

#### Run the built-in demo

```bash
python email_agent.py
```

This runs a sample email through the full pipeline and prints the analysis and draft response to the terminal.

#### Use in your own code

```python
from email_agent import analyze_email, generate_draft_response, process_email

# --- Analyze only ---
email_text = """
Hi, I wanted to follow up on the proposal we discussed last week.
Could you send me the updated pricing by Thursday?
Thanks, Sarah
"""

analysis = analyze_email(email_text)
print(analysis)
# {
#   "intent": "follow-up",
#   "tone": "friendly",
#   "key_points": ["follow-up on proposal", "request for updated pricing", "Thursday deadline"],
#   "urgency": "medium",
#   "action_required": "Send updated pricing by Thursday"
# }

# --- Generate a draft response ---
draft = generate_draft_response(
    email_content=email_text,
    sender_name="Sarah",
    your_name="Alex",
    additional_context="Pricing doc is ready; attach it and confirm delivery.",
)
print(draft)

# --- Full pipeline (analyze + draft in one call) ---
result = process_email(
    email_content=email_text,
    sender_name="Sarah",
    your_name="Alex",
    additional_context="Pricing doc is ready; attach it and confirm delivery.",
)
print(result["analysis"])
print(result["draft_response"])
```

---

### API Reference

#### `analyze_email(email_content: str) -> dict`

Analyzes an email and returns a structured JSON object.

| Field | Type | Description |
|---|---|---|
| `intent` | str | Main purpose of the email (e.g. `"request"`, `"complaint"`) |
| `tone` | str | Emotional tone (e.g. `"formal"`, `"urgent"`, `"friendly"`) |
| `key_points` | list[str] | Up to 3 most important points |
| `urgency` | str | `"low"`, `"medium"`, or `"high"` |
| `action_required` | str | Brief description of the needed response or action |

#### `generate_draft_response(email_content, analysis=None, sender_name="", your_name="", additional_context="") -> str`

Generates a draft email reply. If `analysis` is omitted, it calls `analyze_email()` internally.

#### `process_email(email_content, sender_name="", your_name="", additional_context="") -> dict`

Runs the full pipeline. Returns `{"analysis": {...}, "draft_response": "..."}`.

---

### Model

The agent uses **`gpt-4o-mini`** by default — fast and cost-efficient for email workloads. To switch models, update the `model` parameter in the `client.chat.completions.create()` calls inside `email_agent.py`.

---

### Requirements

- Python 3.10+
- `openai >= 1.12.0`
- An OpenAI API key with access to `gpt-4o-mini`

---

## OpenTelemetry Latency Analyzer

A lightweight, self-contained OpenTelemetry ingestion pipeline that collects
spans in-memory and computes **p50 / p95 / p99** latency statistics — no
external collector required.

### Files

```
├── otel_ingestion.py    # OTel SDK setup, in-memory exporter, span helpers
├── latency_analyzer.py  # Percentile math and formatted report printer
└── demo_otel.py         # End-to-end demo with simulated service calls
```

### How it works

1. **Ingestion** — `otel_ingestion.py` wires up the OpenTelemetry SDK with an
   `InMemorySpanExporter`.  Every span your code emits is captured without
   sending data to any remote backend.
2. **Analysis** — `latency_analyzer.py` groups finished spans by operation
   name and computes `min / mean / p50 / p95 / p99 / max` using pure-Python
   linear-interpolation percentiles (no NumPy).
3. **Demo** — `demo_otel.py` simulates three operations with realistic latency
   distributions (normal, log-normal, cache-hit/miss) and prints the full
   report.

### Quick start

```bash
pip install -r requirements.txt
python demo_otel.py              # 500 simulated requests
python demo_otel.py --count 200  # custom request count
```

Example output:

```
Simulating 500 requests across 3 operations …
Collected 1500 spans.

  OTel Latency Report — 500 simulated requests
  --------------------------------------------------------------------------------------------
  Operation                            Count          Min         Mean          P50       P95 -->          P99          Max
  --------------------------------------------------------------------------------------------
  api.request                            500         5.12        34.87        30.41        148.23       242.10       298.77
  cache.lookup                           500         1.03         9.52         2.41         79.84        98.22       119.45
  db.query                               500        11.24        60.30        54.08        128.19       178.40       231.55
  --------------------------------------------------------------------------------------------
  OVERALL                               1500         1.03        34.90        30.12        128.19       198.30       298.77
  --------------------------------------------------------------------------------------------
  All durations in milliseconds (ms)
```

### API

#### `otel_ingestion.py`

| Symbol | Description |
|---|---|
| `get_tracer(name)` | Returns a tracer backed by the in-memory exporter |
| `record_span(op, ...)` | Context manager — wraps a code block in a span |
| `instrument(op)` | Decorator — wraps a function in a span |
| `get_finished_spans()` | Returns all collected `ReadableSpan` objects |
| `spans_to_records()` | Converts spans to plain dicts for analysis |
| `clear_spans()` | Resets the in-memory store |

#### `latency_analyzer.py`

| Symbol | Description |
|---|---|
| `compute_stats(durations_ms)` | Returns `{count, min, mean, p50, p95, p99, max}` |
| `analyze(records)` | Groups records by operation name and computes stats |
| `analyze_overall(records)` | Aggregate stats across all operations |
| `print_report(records, title)` | Prints a formatted table with bottleneck hints |

### Requirements

- Python 3.10+
- `opentelemetry-api >= 1.20.0`
- `opentelemetry-sdk >= 1.20.0`
