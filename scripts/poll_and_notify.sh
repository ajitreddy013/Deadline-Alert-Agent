#!/usr/bin/env bash
# Poll Gmail + WhatsApp and notify for due-soon tasks
set -euo pipefail

# Configurable settings
BASE_URL="${DEADLINE_BASE_URL:-http://localhost:8000}"
THRESHOLD_MINUTES="${DEADLINE_THRESHOLD_MINUTES:-60}"
CHAT_NAME="${DEADLINE_WHATSAPP_CHAT_NAME:-}"

log() { printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

check_server() {
  if ! curl -sSf "${BASE_URL}/tasks" > /dev/null; then
    log "Backend not reachable at ${BASE_URL}. Skipping run."
    exit 0
  fi
}

urlencode() {
  python3 - <<'PY' "$1"
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1]))
PY
}

run() {
  check_server
  log "Starting poll cycle..."

  # Gmail ingest
  if curl -sS -X POST "${BASE_URL}/ingest/gmail" -o /dev/null; then
    log "Gmail ingested"
  else
    log "Gmail ingest failed"
  fi

  # WhatsApp ingest (optional)
  if [[ -n "${CHAT_NAME}" ]]; then
    ENC_NAME=$(urlencode "${CHAT_NAME}")
    if curl -sS -X POST "${BASE_URL}/ingest/whatsapp?chat_name=${ENC_NAME}" -o /dev/null; then
      log "WhatsApp ingested for chat: ${CHAT_NAME}"
    else
      log "WhatsApp ingest failed for chat: ${CHAT_NAME}"
    fi
  else
    log "CHAT_NAME not set; skipping WhatsApp ingest"
  fi

  # Notify due-soon
  if curl -sS -X POST "${BASE_URL}/notify/due-soon?threshold_minutes=${THRESHOLD_MINUTES}" -o /dev/null; then
    log "Due-soon notifications processed (<= ${THRESHOLD_MINUTES} min)"
  else
    log "Due-soon notifications failed"
  fi

  log "Poll cycle complete."
}

run