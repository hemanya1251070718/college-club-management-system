#!/usr/bin/env bash
# One-command local launcher for ClubHub.
# Usage (from anywhere):  ./start.sh        or   bash start.sh
# Then open http://127.0.0.1:8080
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "Setting up Python environment (first run only)..."
  if command -v uv >/dev/null 2>&1; then
    uv venv -q .venv
    uv pip install -q --python .venv/bin/python -r requirements.txt
  else
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
  fi
fi

echo "Starting ClubHub at http://127.0.0.1:${PORT:-8080}  (Ctrl+C to stop)"
exec .venv/bin/python run.py
