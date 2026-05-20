#!/usr/bin/env bash
# Dev server: sync newStar.svg -> PNG, then serve static site.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-3000}"

"$ROOT/scripts/sync-newstar.sh"

cd "$ROOT"
echo "Serving http://localhost:$PORT (Ctrl+C to stop)"
exec python3 -m http.server "$PORT"
