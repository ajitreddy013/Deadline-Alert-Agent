# Phase 0 — Decisions and Scope

Last updated: 2025-09-30

## Project summary
- Goal: Local, single-user "Deadline Reminder" that ingests deadlines (primarily via WhatsApp Web scraping), stores them locally, and reminds the user via macOS desktop and mobile push notifications.
- Primary UI: Flutter mobile (iOS/Android) first. Secondary: Flutter macOS app; Flutter web is optional later.
- Notifications: macOS native notifications; mobile push via OneSignal; optional WhatsApp outbound via Twilio for later.

## Environment and constraints
- Runtime: macOS development host.
- Backend: FastAPI + SQLite, runs locally on macOS.
- Mobile: Flutter iOS/Android. For local-dev, use simulator/emulator or device on same LAN. Backend reachable via host LAN IP or tunnel if needed.
- Privacy: Local-only processing and storage. No cloud sync in Phase 1.

## Core decisions

### 1) Backend
- Language/Version: Python 3.11+.
- Framework: FastAPI + Uvicorn.
- DB/ORM: SQLite + SQLAlchemy 2.x. Migrations via Alembic (optional in Phase 1; include base migration if straightforward).
- Packaging/Env: uv (latest) for dependency management and locking; python-dotenv for local config.
- Scheduling: APScheduler (or equivalent) to compute and trigger reminders. Rebuild schedule from DB on startup.
- Time parsing: python-dateparser (timezone-aware); default timezone is system timezone.
- CORS: Enabled for development origins (Flutter web if used) and for mobile testing scenarios.
- API (initial):
  - Deadlines CRUD: `GET/POST/PUT/DELETE /deadlines`
  - Reminder view: `GET /reminders` (computed upcoming reminders)
  - WhatsApp ingestion control: `POST /ingestion/whatsapp/start`, `GET /ingestion/whatsapp/status`, `POST /ingestion/whatsapp/stop`
  - Settings: `GET/PUT /settings`
  - Health: `GET /healthz`
- Process model: Single-process app with in-process scheduler for Phase 1. If needed later, split worker process.

Suggested repo structure (Python side):
- `app/api/` — routers (deadlines, settings, ingestion)
- `app/models/` — SQLAlchemy models; Pydantic schemas
- `app/services/` — domain logic (deadlines, reminders, notifications)
- `app/integrations/whatsapp_web/` — Playwright logic for WA Web
- `app/integrations/notifications/` — macOS, OneSignal, Twilio
- `app/scheduler/` — job scheduling helpers
- `app/core/` — config, logging, security helpers

### 2) Data model
Core entities (Phase 1):
- Deadline
  - id (uuid)
  - title (str)
  - description (text, optional)
  - due_at (datetime, tz-aware)
  - status (enum: pending|confirmed|done; default pending for ingested items)
  - priority (enum: low|normal|high|critical; default normal)
  - project (str, optional)
  - source (enum: manual|whatsapp|email)
  - source_ref (str, optional; e.g., chat/message id)
  - source_url (str, optional; e.g., deeplink to WA web message)
  - confidence (float 0–1; for ingested items)
  - tags (comma-separated or join table)
  - created_at, updated_at
- ReminderRule
  - id (uuid)
  - deadline_id (fk)
  - offset_seconds (int; negative means before due time)
  - channel (enum: desktop|mobile|whatsapp)
  - enabled (bool)
- Settings
  - desktop_notifications_enabled (bool)
  - onesignal_enabled (bool), onesignal_app_id, onesignal_rest_api_key (stored locally)
  - twilio_whatsapp_enabled (bool), twilio_account_sid, twilio_auth_token, twilio_whatsapp_from
  - whatsapp_scraping: headless (bool), user_data_dir (path)

### 3) Default reminder policy
- Defaults: −24h and at due time (0). User can edit per deadline.
- Channels by default:
  - Desktop (macOS): on
  - Mobile (OneSignal): on (if configured)
  - WhatsApp outbound (Twilio): off by default

### 4) Notifications
- macOS desktop: Use `pync` (terminal-notifier under the hood). Fallback via AppleScript if required.
- Mobile push: OneSignal integration included in Phase 1 (mobile-first). Store keys locally via environment or settings API. Respect platform requirements (APNs for iOS, FCM for Android) and allow app to run with push disabled if credentials are absent.
- WhatsApp outbound (optional): Twilio WhatsApp API for self-reminders; gated by config.

### 5) UI (Flutter) — mobile first
- Targets: iOS and Android in Phase 1. macOS app optional; Flutter web later.
- State: Riverpod; Networking: dio (or http).
- Views:
  - Home: upcoming deadlines list; search/filter; quick snooze/confirm/done.
  - Detail: edit title/description/due time/reminders/priority/project.
  - Add/Edit: create/update deadlines.
  - Settings: toggle channels; input OneSignal/Twilio config; control WhatsApp ingestion (start/stop, status).
  - Inbox: review queue for ingested candidates (pending status) to confirm or reject.
- Connectivity:
  - Base URL configurable. For iOS Simulator, `http://127.0.0.1:8000`; for Android Emulator, `http://10.0.2.2:8000`; for real devices, use host LAN IP or tunnel.

### 6) WhatsApp ingestion (Web scraping)
- Tech: Playwright for Python with Chromium persistent user profile at `~/.deadline_reminder/whatsapp`.
- Login: QR code login if needed; session persists locally.
- Capture scope: Capture every likely deadline (no capture token required). Heuristics-driven detection to minimize false positives.
- Heuristics (initial):
  - Keyword patterns: `deadline`, `due`, `submit`, `submit by`, `by <time>`, `register`, `apply`, `fill the form`, `form due`.
  - Date/time extraction via dateparser; associate nearest date/time phrase to action keywords.
  - Confidence scoring: increase with presence of strong keywords (`deadline`, `due`, `submit by`) and explicit date/time; decrease for forwarded/system messages.
  - Minimum confidence threshold creates a "pending" Deadline; user confirmation moves to "confirmed".
- Controls: API to start/stop watcher; UI shows status; manual refresh.
- Reliability: Centralize selectors and add health checks. Expect DOM changes; provide structured logs and fallback instructions.
- ToS: Scraping may violate WhatsApp ToS; user acknowledges risk. Local use only.

### 7) Email ingestion (future)
- Plan: Add IMAP watcher to parse emails for deadlines (e.g., keywords and date detection similar to WA). Not in Phase 1 deliverable unless explicitly prioritized.

### 8) Security & privacy
- Local-only data; no cloud sync.
- Secrets via environment variables or local encrypted storage; never log secrets.
- Logs redact message contents by default; optional verbose mode for troubleshooting.

### 9) Out of scope (Phase 1)
- Multi-user/auth, cloud sync, sharing.
- Advanced NLP/ML beyond heuristics + date parsing.
- Complex recurrence rules (simple offsets only).

### 10) Risks and mitigations
- WhatsApp DOM changes → Abstract selectors; add self-check and quick patch instructions.
- False positives in ingestion → Pending review inbox + confidence scores; allow fast reject and incremental keyword tuning.
- Notification permissions → First-run prompts; graceful degradation if denied.
- Mobile connectivity to local backend → Document simulator/emulator hostnames; add configurable base URL; suggest tunnels for devices.
- Time parsing ambiguity → Surface parsed result; editable before save; locale/timezone-aware parsing.

---

## Phase 1 deliverables
- FastAPI service with SQLite schema, CRUD for deadlines, reminder scheduling, and macOS desktop notifications.
- WhatsApp Web ingestion via Playwright with QR login, background watcher, heuristics-based detection, confidence scoring, and pending review queue.
- Flutter mobile app (iOS/Android): Home, Detail, Add/Edit, Settings, Inbox views; REST integration.
- OneSignal mobile push integration (feature-flagged via settings; app runs without keys).
- Configuration via `.env` or settings API; basic setup docs.

## Phase 1 milestones (high level)
1) Backend foundation (FastAPI, models, migrations, CRUD) — 1.5–2 days
2) Scheduler + desktop notifications — 0.5–1 day
3) WhatsApp Playwright integration (login, session, basic scrape) — 1–2 days
4) Ingestion heuristics + confidence + review inbox API — 1–1.5 days
5) Flutter mobile app (base nav, views, REST wiring) — 2–3 days
6) OneSignal integration (mobile push) — 1–1.5 days (requires platform creds)
7) Polish: settings, error handling, logs, docs — 0.5–1 day

Total initial estimate: ~7–12 days depending on credentials and iteration on heuristics.

## Implementation notes
- Python deps via uv: `uv venv && uv pip install fastapi uvicorn sqlalchemy dateparser apscheduler pydantic-settings playwright pync python-dotenv` (exact list to be finalized).
- Playwright: `playwright install chromium` on first setup.
- macOS notifications: ensure `terminal-notifier` is available (pync will manage or install separately).
- Mobile push: OneSignal requires APNs (iOS) and FCM (Android) configuration; app should degrade gracefully if not configured.

## Open items
- Email ingestion is noted for a future phase.
