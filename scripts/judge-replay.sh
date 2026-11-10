#!/bin/sh
# Keyless public-package check; the pinned driver uses Docker, not Compose.
set -eu

if ! command -v uv >/dev/null 2>&1; then
    printf '%s\n' 'uv is required. Install uv first; see INSTALL.md. No image or model is downloaded by this shell entry.' >&2
    exit 1
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$script_dir/.."
exec uv run python scripts/judge_replay.py "$@"
