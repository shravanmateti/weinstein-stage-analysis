"""Offline stand-in for yfinance: serves weekly prices from data/price_cache.pkl.

Used by tools/run_offline.sh so the backtest can be re-run on the exact data
snapshot in this repo (no internet needed).
"""
from pathlib import Path

import pandas as pd

_CACHE = pd.read_pickle(Path(__file__).resolve().parents[2] / "data" / "price_cache.pkl")


def download(ticker, **kwargs):
    df = _CACHE.get(ticker.replace(".NS", ""))
    return pd.DataFrame() if df is None else df.copy()
