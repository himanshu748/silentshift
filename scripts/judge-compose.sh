#!/bin/sh
# Source-only Compose setup plus unchanged native keyless replay assertions.
set -eu
if ! command -v uv >/dev/null 2>&1; then
    printf '%s\n' 'uv is required. Follow INSTALL.md first; this entry never downloads IRIS or a model.' >&2
    exit 1
fi
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$script_dir/.."
exec uv run python scripts/judge_compose.py "$@"
