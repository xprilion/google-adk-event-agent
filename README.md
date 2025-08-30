## Events Agent

A minimal FastAPI service that exposes a tools-enabled agent for querying a catalog of events. The agent loads a local JSON dataset (`data/all-events.json`), normalizes fields (dates, tags), and provides a `get_events` tool with filters.

### Prerequisites

- Python 3.11+ (3.12 recommended)
- pip
- Optional: Docker

### Quick start (local)

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Fetch the dataset to `data/all-events.json`

```bash
mkdir -p data
# You can change EVENTS_URL if you have a different source
EVENTS_URL=${EVENTS_URL:-https://developers.events/all-events.json}
curl -L "$EVENTS_URL" -o data/all-events.json
```

4. Run the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

- The agent will load events from `data/all-events.json` at import time. You can override the data directory by setting `DATA_DIR` (defaults to `<repo>/data`).

### Quick usage (Python)

```python
from event_agent.agent import get_events

# Example: find Budapest conferences in Hungary
result = get_events(query="conf", city="budapest", country="hungary")
print(result)
```

### Docker

Build and run (ensure `data/all-events.json` exists locally first):

```bash
docker build -t events-agent .
# Mount local data so the container can read it
docker run --rm -p 8080:8080 -v "$(pwd)/data:/app/data" events-agent
```

### Configuration

- DATA_DIR: Directory containing `all-events.json` (default: `<repo>/data`).
- EVENTS_URL: Used only during dataset fetch (see Quick start step 3). The API itself reads from the local file.

### Troubleshooting

- "Events file not found": Make sure `data/all-events.json` exists (see Quick start step 3) or set `DATA_DIR` to the folder containing it.
