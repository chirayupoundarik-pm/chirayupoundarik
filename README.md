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
