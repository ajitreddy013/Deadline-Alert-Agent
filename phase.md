# Phased Plan to Complete the “Deadline Reminder” Project

This plan breaks the work into small, verifiable phases with clear goals and acceptance criteria.

## Phase 0: Repo health, environment, and alignment
- Goals:
  - Ensure the project runs end-to-end locally (backend + Flutter app).
  - Align documentation and code around the chosen push-notification provider (OneSignal vs. FCM).
  - Clean up untracked changes and ensure consistent dependency management.
- Actions:
  - Backend: create `backend/.env` from `backend/.env.template`; confirm `DATABASE_URL` and Gmail credentials work.
  - Push provider alignment:
    - Current state uses OneSignal in Flutter; backend supports both OneSignal and FCM.
    - Decide: OneSignal primary (recommended) and make FCM optional or remove it.
    - Update `README.md` and docs to reflect the decision (remove or mark Firebase references as optional/legacy).
  - Dependencies:
    - Choose either `backend/requirements.txt` or `pyproject.toml` as the source of truth; align versions across both or remove the unused one (spaCy model is pinned in requirements.txt).
    - Add a Makefile or simple scripts for setup (install, run, test).
  - Version control hygiene: commit untracked files in `backend/scripts/`, `backend/fcm_notify.py`, etc., or delete if obsolete.
- Acceptance criteria:
  - `python backend/run_server.py` starts backend at http://localhost:8000 and `/docs` loads.
  - `deadline_alert_app` runs and lists tasks from `GET /tasks`.
  - `README.md` reflects the chosen push provider consistently.
  - One clear dependency setup path works on a clean machine.

## Phase 1: Backend stabilization and API completeness
- Goals:
  - Harden core endpoints, ensure DB schema is stable, and fill obvious gaps.
- Actions:
  - Verify `models.py` contains `Task`, `UserPreferences`, and `DeviceToken` tables used by `app.py`. Add Alembic or document a migration/reset process.
  - Normalize deadline parsing:
    - Ensure `dateparser` is consistently imported and used where relevant.
    - Store canonical ISO 8601 timestamps where possible; optionally keep original text.
  - Implement or verify missing endpoints referenced in docs:
    - If multi-email ingest is desired (per `MULTI_EMAIL_SETUP.md`), add `POST /ingest/multi-gmail` and code to ingest all configured accounts.
  - Add `PATCH /tasks/{id}` for updates (mark complete, update deadline, etc.).
  - Add simple API key auth for write endpoints (optional now; see Phase 8).
- Acceptance criteria:
  - CRUD on tasks works; ingest from Gmail and WhatsApp creates tasks.
  - Deadlines parsed consistently and comparable across time zones.
  - Multi-email ingest exists if desired, or docs updated to remove it.

## Phase 2: Ingestion pipeline robustness
- Goals:
  - Make Gmail and WhatsApp ingestion reliable and predictable.
- Actions:
  - Gmail:
    - Add account config loader (`email_accounts.json`) and validation script (as implied in docs).
    - Add rate limiting/backoff and better error handling for IMAP failures.
  - WhatsApp:
    - Improve Selenium selectors’ fallbacks, login wait, and error messages (already started in `whatsapp_ingest.py`).
    - Optional: run headless only if a session exists; otherwise visible for QR.
    - Provide helper scripts like `backend/scripts/ingest_whatsapp.sh` and document usage.
- Acceptance criteria:
  - `POST /ingest/gmail` and `POST /ingest/whatsapp` return structured errors on failure and produce tasks when patterns are found.
  - WhatsApp: first run requires QR; subsequent runs do not.

## Phase 3: Notifications (Desktop + Mobile)
- Goals:
  - Finalize the push notification architecture and UX.
- Actions:
  - OneSignal as primary:
    - Document how the Flutter app registers its `player_id` and how/when backend uses it.
    - Ensure a token registration endpoint stores OneSignal `player_id` (repurpose `/register_token` or add `/register_player`).
    - Make `/notify/mobile` use OneSignal by default; mark `/notify/mobile/fcm` optional/legacy (or remove).
  - Desktop:
    - Confirm `/notify/due-soon` works; fix imports if needed; ensure `alert_status` transitions to `sent`.
- Acceptance criteria:
  - Mobile notifications received on device via OneSignal (manual test).
  - Desktop notifications trigger reliably for due-soon tasks.

## Phase 4: Scheduling and automation
- Goals:
  - Make the system proactive without manual triggers.
- Actions:
  - Add APScheduler job(s) to run due-soon checks every N minutes within the backend (or a separate worker).
  - Optional: cron or launchd for macOS if you prefer external scheduling.
  - Optional: schedule Gmail ingestion (e.g., every 10–15 minutes).
- Acceptance criteria:
  - Without manual calls, tasks are ingested on a schedule (if enabled) and due-soon notifications fire.

## Phase 5: Flutter app polish
- Goals:
  - Provide a complete mobile UX for viewing and managing deadlines.
- Actions:
  - Settings screen:
    - Backend base URL (persisted).
    - Notification preferences (desktop/mobile/WhatsApp) wired to `/user/preferences`.
    - WhatsApp number entry/validation with immediate feedback using backend validation.
  - Task detail and management:
    - Task detail view; mark complete; edit deadline; filter by source (gmail/whatsapp).
  - Notification handling:
    - Ensure OneSignal handling shows in-app banners, deep links to task detail, and background handling.
  - Add simple theming and accessibility basics.
- Acceptance criteria:
  - End-to-end flow: ingest → task visible → edit/complete → notifications reflect state.
  - Settings changes persist and apply.

## Phase 6: Testing and quality gates
- Goals:
  - Confidence in reliability and prevention of regressions.
- Actions:
  - Backend tests:
    - Unit tests for extraction, parsing, and models.
    - Integration tests for API endpoints with a test DB.
    - Mocked Gmail/WhatsApp inputs for ingestion tests.
  - Flutter tests:
    - Widget tests for `TaskListScreen`.
    - Optional integration test hitting local backend.
  - CI:
    - GitHub Actions: Python tests + Flutter tests; cache deps; fail on lint/test errors.
  - Linters/formatters:
    - Python: Black, Ruff (or just Ruff), isort.
    - Dart: `flutter format`, `flutter analyze`.
- Acceptance criteria:
  - CI green on PRs; tests cover core API and UI flows; minimum coverage threshold is agreed and met.

## Phase 7: Packaging and run scripts
- Goals:
  - Make running and sharing the project simple.
- Actions:
  - Provide scripts:
    - `scripts/dev_bootstrap.sh` (install deps, download spaCy model).
    - `scripts/run_backend.sh` and `scripts/run_all.sh`.
    - `scripts/ingest_whatsapp.sh` and `scripts/ingest_gmail.sh`.
  - Optional Docker:
    - Backend Dockerfile with spaCy model preinstalled.
    - `docker-compose.yml` for backend and optionally a Selenium Chrome container.
- Acceptance criteria:
  - New contributors can bootstrap and run with one or two commands.
  - Optional: `docker compose up` starts backend; docs cover WhatsApp caveats.

## Phase 8: Security and privacy hardening
- Goals:
  - Protect credentials and personal data; ensure safe-by-default configuration.
- Actions:
  - API access:
    - Optional local API key for write/ingestion endpoints.
    - Tighten CORS to only necessary origins.
  - Secrets:
    - Ensure `.env.example` and `deadline_alert_app/.env.example` are accurate, and secrets are never logged.
  - Data:
    - PII-safe logs; configurable retention.
- Acceptance criteria:
  - No secrets in logs; restricted CORS; optional API key works and is documented.

## Phase 9: Documentation, cleanup, and release
- Goals:
  - Finalize docs and tag the release.
- Actions:
  - Update README to reflect final architecture (OneSignal-first), current endpoints, and accurate Quick Start.
  - Reconcile `MULTI_EMAIL_SETUP.md` and `WHATSAPP_INTEGRATION_GUIDE.md` with actual endpoints and behavior.
  - Add `CHANGELOG.md` and tag `v1.0.0`.
- Acceptance criteria:
  - Docs match the code; a newcomer can follow them and succeed.
  - `v1.0.0` tag created; repo clean with no TODOs left in docs.

---

## Optional stretch goals
- Web UI (Flutter web) for quick desktop usage.
- Advanced NLP patterns for better deadline extraction and normalization.
- Analytics view: counts by source, upcoming week view, snooze flows.
- WhatsApp Business API integration for production-grade messaging (replace Selenium scraping and Twilio sandbox limitations).

## Suggested immediate next steps
1) Decide push provider direction (OneSignal primary; FCM optional or removed).
2) Align README and dependencies accordingly.
3) Implement scheduling (APScheduler) for due-soon checks and optionally Gmail ingest.
4) Add settings and preferences flow in Flutter and wire to backend endpoints.
5) Add core tests and a simple CI workflow.
