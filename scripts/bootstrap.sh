#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if command -v uv >/dev/null 2>&1; then
    exec uv run python scripts/bootstrap.py "$@"
fi
exec python3 scripts/bootstrap.py "$@"
