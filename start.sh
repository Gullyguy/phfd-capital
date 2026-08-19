#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PHFD_ADMIN_USER="${PHFD_ADMIN_USER:-admin}"
export PHFD_ADMIN_PASSWORD="${PHFD_ADMIN_PASSWORD:-change-me-now}"
export LIVE_PROVIDER_MODE="${LIVE_PROVIDER_MODE:-false}"
export PHFD_DB_PATH="${PHFD_DB_PATH:-/tmp/phfd-capital/phfd_capital.db}"
exec uvicorn app:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
