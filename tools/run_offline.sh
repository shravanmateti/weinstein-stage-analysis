#!/bin/sh
# Re-run the backtest on the saved price snapshot (data/price_cache.pkl), no internet needed.
# Output CSVs are written to the current folder.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHONPATH="$ROOT/tools/yfinance_offline" python3 "$ROOT/backtest/stage_backtest.py" "$ROOT/data/Stage_S2_Analysis_2026-10-01.xlsx" --years 10
