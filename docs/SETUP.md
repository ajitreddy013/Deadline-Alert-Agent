# Setup

## Prereqs
- Python 3.11+
- uv (https://github.com/astral-sh/uv) or pip
- Playwright browsers (Chromium)

## Install deps

Using uv:

```bash
uv venv
uv pip install -e .
python -m playwright install chromium
```

Or using pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m playwright install chromium
```

Copy `.env.example` to `.env` and fill in any keys you have.

## Run backend

```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://127.0.0.1:8000/docs for the API docs.

## Start WhatsApp ingestion (manual)
- Call POST /ingestion/whatsapp/start
- Scan QR in the opened Chromium profile if prompted.
- Call GET /ingestion/whatsapp/status to check state.

## Notes
- Default reminders are set to −24h and at due time for each new deadline on desktop and mobile channels. Mobile notifications require OneSignal configuration.
- macOS notifications use pync/terminal-notifier; allow notification permissions when prompted.
