#!/usr/bin/env bash
# Smoke test + đấu local vs random. Dùng: bash scripts/run_local.sh [số_game]
set -e
cd "$(dirname "$0")/.."
GAMES="${1:-3}"

echo "== Smoke test: import agent + chạy 1 turn =="
python tests/smoke_test.py

echo
echo "== $GAMES game vs random =="
python tests/test_local.py --games "$GAMES"
