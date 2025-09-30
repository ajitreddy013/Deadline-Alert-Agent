#!/usr/bin/env bash
set -euo pipefail

# Minimal test for Phase 7 — Mobile push via OneSignal
# Requirements:
# - Backend running at http://localhost:8000 (from backend/run_server.py)
# - backend/.env has ONESIGNAL_APP_ID and ONESIGNAL_API_KEY set
# - PLAYER_ID exported from your device (OneSignal SDK on the app returns this)
#
# Usage:
#   export PLAYER_ID="<your-onesignal-player-id>"
#   ./scripts/test_mobile_push.sh "Title here" "Message here"

if [[ -z "${PLAYER_ID:-}" ]]; then
  echo "PLAYER_ID env var is not set. Please export your OneSignal player_id from the device."
  exit 1
fi

TITLE=${1:-"Test Notification"}
MESSAGE=${2:-"Hello from Deadline Reminder"}

curl -sS -X POST \
  "http://localhost:8000/notify/mobile?player_id=${PLAYER_ID}&title=$(printf %s "$TITLE" | sed 's/ /%20/g')&message=$(printf %s "$MESSAGE" | sed 's/ /%20/g')"
