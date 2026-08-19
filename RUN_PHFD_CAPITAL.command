#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f data/phfd_capital.db ]; then
  python seed_demo.py
fi
export PHFD_ADMIN_USER="${PHFD_ADMIN_USER:-admin}"
export PHFD_ADMIN_PASSWORD="${PHFD_ADMIN_PASSWORD:-change-me-now}"
( sleep 2; command -v open >/dev/null && open http://localhost:8000 ) &
./start.sh
