"""Backtest of weinstein-stage-analysis-v1.pine (weekly chart, Investor exit) on a stock list.

Usage (needs internet access to Yahoo Finance):
    pip install yfinance pandas openpyxl
    python stage_backtest.py Stage_S2_Analysis_2026-10-01.xlsx --years 10

Writes backtest_trades.csv, backtest_by_stock.csv and prints a summary.
Each tranche is the same rupee amount. A trade = ENTER through EXIT (or still open at the end).
"""
import argparse
import sys

import numpy as np
import pandas as pd

# ---- v1 defaults (weekly chart) ----
MA_LEN, FAST_LEN, SLOPE_LEN, FLAT = 30, 10, 4, 0.5
BASE_LEN, CONFIRM = 10, 2
VOL_LEN, VOL_MULT = 30, 2.0
MAX_TRANCHES, COOL, ENTRY_WIN, ZONE = 3, 3, 4, 3.0


def run(df):
    """df: weekly OHLCV with columns Open High Low Close Volume. Returns list of trades."""
    o, h, l, c, v = (df[k].to_numpy(float) for k in ["Open", "High", "Low", "Close", "Volume"])
    n = len(c)
    ma = pd.Series(c).rolling(MA_LEN).mean().to_numpy()
    fast = pd.Series(c).rolling(FAST_LEN).mean().to_numpy()
    volma = pd.Series(v).rolling(VOL_LEN).mean().to_numpy()
    base_high = pd.Series(h).rolling(BASE_LEN).max().shift(1).to_numpy()
    ma_back = pd.Series(ma).shift(SLOPE_LEN).to_numpy()
    ma_long = pd.Series(ma).shift(MA_LEN).to_numpy()

    stage, stage_start, s_hi, s_lo, bo_level, ma_rose = 0, None, np.nan, np.nan, np.nan, False
    since_rise = since_fall = 10**6
    in_pos, tranches, last_buy, entry_px = False, 0, None, np.nan
    buys, trades, prev_vr = [], [], 1.0

    for i in range(n):
        vr = v[i] / volma[i] if volma[i] and volma[i] > 0 else 0.0
        hi_vol, light_vol = vr >= VOL_MULT, vr < 1.0
        slope = (ma[i] - ma_back[i]) / ma_back[i] * 100 if not np.isnan(ma_back[i]) else np.nan
        rising = bool(slope > FLAT) if not np.isnan(slope) else False
        falling = bool(slope < -FLAT) if not np.isnan(slope) else False
        since_rise = 0 if rising else since_rise + 1
        since_fall = 0 if falling else since_fall + 1
        gt = lambda a, b: (not np.isnan(a)) and (not np.isnan(b)) and a > b
        lt = lambda a, b: (not np.isnan(a)) and (not np.isnan(b)) and a < b
        trend_up = gt(c[i], ma[i]) and rising
        trend_down = lt(c[i], ma[i]) and falling

        new = stage
        if np.isnan(ma_back[i]):
            new = 0
        elif stage == 0:
            new = 2 if trend_up else 4 if trend_down else (3 if gt(ma[i], ma_long[i]) else 1)
        elif stage == 1:
            if (gt(c[i], base_high[i]) and gt(c[i], ma[i]) and not falling) or trend_up:
                new = 2
            elif lt(c[i], s_lo) and lt(c[i], ma[i]) and not rising:
                new = 4
        elif stage == 2:
            if trend_down:
                new = 4
            elif not ma_rose and lt(c[i], ma[i]):
                new = 1
            elif ma_rose and (since_rise >= CONFIRM or (lt(c[i], ma[i]) and not rising)):
                new = 3
        elif stage == 3:
            if (lt(c[i], s_lo) and lt(c[i], ma[i])) or trend_down:
                new = 4
            elif gt(c[i], s_hi) and gt(c[i], ma[i]) and rising:
                new = 2
        elif stage == 4:
            if since_fall >= CONFIRM:
                new = 1

        prev = stage
        if new != stage:
            if new == 2:
                bo_level = np.nan if prev == 0 else s_hi
            stage, stage_start, s_hi, s_lo, ma_rose = new, i, h[i], l[i], rising
        else:
            s_hi = h[i] if np.isnan(s_hi) else max(s_hi, h[i])
            s_lo = l[i] if np.isnan(s_lo) else min(s_lo, l[i])
            ma_rose = ma_rose or rising

        # EXIT (Investor): close below 30-week MA or Stage 4
        exited = False
        if in_pos and (lt(c[i], ma[i]) or stage == 4):
            trades.append(close_trade(df, buys, i, c[i], "exit"))
            in_pos, tranches, buys, entry_px, exited = False, 0, [], np.nan, True

        # ENTER
        entered = False
        if not in_pos and not exited and not np.isnan(bo_level) and stage == 2:
            in_win = i - stage_start <= ENTRY_WIN
            breakout = in_win and c[i] > bo_level and hi_vol
            retest = l[i] <= bo_level * (1 + ZONE / 100) and c[i] >= bo_level and light_vol
            if breakout or retest:
                in_pos, tranches, last_buy, entry_px, entered = True, 1, i, c[i], True
                buys = [(i, c[i])]

        # ADD
        if in_pos and not entered and stage == 2 and tranches < MAX_TRANCHES and i - last_buy >= COOL \
                and c[i] > entry_px and gt(c[i], fast[i]):
            pullback = l[i] <= fast[i] * (1 + ZONE / 100) and c[i] > o[i] and (light_vol or prev_vr < 1.0)
            new_high = gt(c[i], base_high[i]) and hi_vol
            if pullback or new_high:
                tranches += 1
                last_buy = i
                buys.append((i, c[i]))
        prev_vr = vr

    if in_pos:
        trades.append(close_trade(df, buys, n - 1, c[-1], "open"))
    return trades


def close_trade(df, buys, i, px, status):
    cost = len(buys)                      # 1 unit of money per tranche
    value = sum(px / b for _, b in buys)  # value of those units now
    return {
        "entry_date": df.index[buys[0][0]].date(), "exit_date": df.index[i].date(),
        "entry_px": round(buys[0][1], 2), "exit_px": round(px, 2), "tranches": len(buys),
        "weeks": i - buys[0][0], "return_pct": round((value / cost - 1) * 100, 2), "status": status,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--suffix", default=".NS", help="Yahoo suffix: .NS for NSE, .BO for BSE")
    a = ap.parse_args()
    import yfinance as yf

    stocks = pd.read_excel(a.xlsx)
    rows, by_stock = [], []
    for sym in stocks["Symbol"].dropna().astype(str).str.strip():
        try:
            df = yf.download(sym + a.suffix, period=f"{a.years}y", interval="1wk", auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna()
            if len(df) < MA_LEN + SLOPE_LEN + 5:
                by_stock.append({"symbol": sym, "trades": 0, "note": "not enough history"})
                continue
            t = run(df)
            for x in t:
                x["symbol"] = sym
            rows += t
            r = [x["return_pct"] for x in t]
            by_stock.append({"symbol": sym, "trades": len(t), "wins": sum(x > 0 for x in r),
                             "avg_return_pct": round(np.mean(r), 2) if r else None,
                             "total_return_pct": round((np.prod([1 + x / 100 for x in r]) - 1) * 100, 2) if r else None})
        except Exception as e:  # keep going on bad symbols
            by_stock.append({"symbol": sym, "trades": 0, "note": f"error: {e}"})
        print(f"{sym}: {by_stock[-1].get('trades', 0)} trades", file=sys.stderr)

    tr = pd.DataFrame(rows)
    pd.DataFrame(by_stock).to_csv("backtest_by_stock.csv", index=False)
    tr.to_csv("backtest_trades.csv", index=False)
    if tr.empty:
        print("No trades.")
        return
    closed = tr[tr.status == "exit"]
    for name, d in [("All trades (open ones marked to last price)", tr), ("Closed trades only", closed)]:
        if d.empty:
            continue
        w, lo = d[d.return_pct > 0], d[d.return_pct <= 0]
        print(f"\n== {name} ==")
        print(f"Trades: {len(d)}   Win rate: {len(w) / len(d) * 100:.1f}%")
        print(f"Avg return/trade: {d.return_pct.mean():.2f}%   Median: {d.return_pct.median():.2f}%")
        print(f"Avg win: {w.return_pct.mean():.2f}%   Avg loss: {lo.return_pct.mean():.2f}%")
        if len(lo) and lo.return_pct.sum() != 0:
            print(f"Profit factor: {w.return_pct.sum() / -lo.return_pct.sum():.2f}")
        print(f"Avg holding: {d.weeks.mean():.1f} weeks   Avg tranches: {d.tranches.mean():.2f}")


if __name__ == "__main__":
    main()
