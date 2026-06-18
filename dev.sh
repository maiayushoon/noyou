#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NoYou — one-command dev launcher (macOS / Linux)
#   Starts the FastAPI backend on :8000 and the Next.js dashboard on :3002.
#   Run:  ./dev.sh     Stop: Ctrl+C (kills both).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Free the ports so nothing drifts.
for port in 8000 3002; do
  lsof -ti "tcp:$port" 2>/dev/null | xargs -r kill -9 2>/dev/null || true
done

echo "  Starting backend   -> http://localhost:8000"
( cd "$ROOT" && backend/venv/bin/uvicorn app.main:app --app-dir backend --reload --reload-dir backend --port 8000 ) &
BACK=$!

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "  Installing dashboard deps (first run)..."
  ( cd "$ROOT/frontend" && npm install )
fi
echo "  Starting dashboard -> http://localhost:3002"
( cd "$ROOT/frontend" && npm run dev ) &
FRONT=$!

echo ""
echo "  NoYou dev is up:"
echo "    Dashboard : http://localhost:3002   (demo@noyou.app / demo12345)"
echo "    API       : http://localhost:8000   (docs at /docs)"
echo ""
trap 'echo "stopping..."; kill $BACK $FRONT 2>/dev/null || true' EXIT INT TERM
wait
