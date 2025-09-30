#!/usr/bin/env bash
set -euo pipefail

# Minimal test for Phase 7 — Mobile push via FCM (legacy HTTP)
# Requirements:
# - Backend running at http://localhost:8000 (from backend/run_server.py)
# - backend/.env has FCM_SERVER_KEY set
# - DEVICE_TOKEN exported from your device (returned by Firebase Messaging SDK)
#
# Usage:
#   export DEVICE_TOKEN="<your-fcm-device-token>"
#   ./scripts/test_mobile_push_fcm.sh "Title here" "Message here"

if [[ -z "${DEVICE_TOKEN:-}" ]]; then
  echo "DEVICE_TOKEN env var is not set. Please export your FCM device token from the app."
  exit 1
fi

TITLE=${1:-"Test Notification (FCM)"}
MESSAGE=${2:-"Hello from Deadline Reminder via FCM"}

curl -sS -X POST \
  "http://localhost:8000/notify/mobile/fcm?device_token=$(printf %s "$DEVICE_TOKEN" | sed 's/ /%20/g')&title=$(printf %s "$TITLE" | sed 's/ /%20/g')&message=$(printf %s "$MESSAGE" | sed 's/ /%20/g')"