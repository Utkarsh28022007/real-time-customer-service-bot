#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================"
echo "  Starting NovaTech AI Customer Service Bot"
echo "========================================================"

if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "[*] Starting FastAPI Backend on http://localhost:8000..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "[*] Starting Vite Frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "========================================================"
echo "  Application running!"
echo "  - Chat & Admin UI: http://localhost:5173"
echo "  - Backend API & Docs: http://localhost:8000/docs"
echo "========================================================"

wait
