#!/usr/bin/env bash
set -euo pipefail

# Simple helper to trigger WhatsApp ingestion by chat name
# Usage: backend/scripts/ingest_whatsapp.sh "Family"  OR  "Work Group"

BASE_URL="${BASE_URL:-http://localhost:8000}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") \"Chat Name\"" >&2
  exit 1
fi

CHAT_NAME="$*"

echo "Starting WhatsApp ingestion for chat: \"$CHAT_NAME\""
echo "If a browser opens with a QR code, scan it with WhatsApp on your phone."

curl -sS -X POST "$BASE_URL/ingest/whatsapp" --get --data-urlencode "chat_name=$CHAT_NAME"
