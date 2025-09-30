#!/usr/bin/env bash
set -euo pipefail

# Simple SQLite backup script
# Usage: ./scripts/backup_db.sh [DB_PATH] [BACKUP_DIR]
# Defaults: DB_PATH=backend/tasks.db, BACKUP_DIR=backups

DB_PATH=${1:-backend/tasks.db}
BACKUP_DIR=${2:-backups}

mkdir -p "$BACKUP_DIR"
TS=$(date +%Y%m%d-%H%M%S)
BASENAME=$(basename "$DB_PATH")
NAME_NO_EXT="${BASENAME%.db}"
TARGET_DB="$BACKUP_DIR/${NAME_NO_EXT}-$TS.db"

if [ ! -f "$DB_PATH" ]; then
  echo "Error: Database not found at $DB_PATH" >&2
  exit 1
fi

# Prefer SQLite's online backup to ensure consistency
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$DB_PATH" ".backup '$TARGET_DB'"
else
  # Fallback to a regular copy
  cp "$DB_PATH" "$TARGET_DB"
fi

gzip -9 "$TARGET_DB"

printf "Backup created: %s.gz\n" "$TARGET_DB"
