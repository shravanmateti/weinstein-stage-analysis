# Stage 2 screen on screener.in + TradingView checklist

Workflow: **screener.in finds candidates → the v1 indicator on a weekly TradingView chart decides ENTER / ADD / HOLD / EXIT.**

> Ratio names below are the ones screener.in normally uses. Type the first few letters in the query box and pick the exact name from its autocomplete. If a name differs, swap it in.

## 1. What screener.in can and can't check

| v1 indicator rule | screener.in | How to cover it |
|---|---|---|
| Price above the 30-week (150-day) MA | ⚠️ no 150-day MA | Use DMA 50 and DMA 200 as a proxy |
| 30-week MA rising | ⚠️ only a 1-day slope (`DMA 200` vs `DMA 200 previous day`) | Proxy, then confirm visually |
| MA rising for 4+ weeks, not just flat | ❌ | **TradingView** |
| A Stage 1 base came before the breakout | ❌ | **TradingView** |
| Breakout above the base top | ⚠️ partly, via nearness to the 52-week high | Proxy, then confirm visually |
| Breakout week volume ≥ 2× average | ⚠️ daily volume only | Proxy, then confirm on the weekly chart |
| Weeks since Stage 2 started (ENTER window) | ❌ | **TradingView** (the "S2 start" label) |
| Not churning or topping (Stage 3) | ❌ | **TradingView** |
| Liquidity and size | ✅ | Market cap and volume filters |
| Momentum and relative strength | ⚠️ absolute returns only, no RS vs Nifty | Return filters |

## 2. The query (paste into screener.in → Screens → Create new screen)

**A. Core Stage 2 screen (broad list)**

```
Current price > DMA 50 AND
DMA 50 > DMA 200 AND
DMA 200 > DMA 200 previous day AND
DMA 50 > DMA 50 previous day AND
Current price > Low price * 1.3 AND
Current price > High price * 0.75 AND
Return over 6months > 10 AND
Market Capitalization > 500 AND
Volume 1month average * Current price > 10000000
```

| Line | Why |
|---|---|
| Price > DMA 50 > DMA 200 | Moving averages stacked in an uptrend (the closest proxy for "above a rising 30-week MA") |
| DMA 200 and DMA 50 above their previous-day values | Long and short MAs both rising |
| ≥ 30% above the 52-week low | Has clearly left the Stage 4 / Stage 1 lows |
| Within 25% of the 52-week high | Near the highs, not stuck in a base or falling |
| 6-month return > 10% | Positive momentum |
| Market cap > ₹500 Cr, daily turnover > ₹1 Cr | Tradeable; avoids illiquid microcaps. Raise these if you want fewer stocks |

**B. Fresh-breakout screen (stocks that may be inside the ENTER window)**

Add these lines to screen A:

```
Current price > High price * 0.95 AND
Volume 1week average > Volume 1month average * 1.5
```

Price is within 5% of the 52-week high, and volume is expanding. These are the stocks most likely to show a fresh ENTER signal.

## 3. What to check visually in TradingView (weekly chart, v1 indicator on)

For each candidate, go through this list in order. Skip the stock as soon as one check fails.

1. **Stage label.** The background is green (Stage 2), not orange (Stage 3).
2. **Weeks since "S2 start".** 4 weeks or fewer means a breakout ENTER is still possible. More than 4 means wait for a retest ENTER (a light-volume pullback to the breakout level).
3. **A real base before it.** There should be a grey Stage 1 period of several months, with the 30-week MA flat beforehand. A V-shaped spike with no base is weaker.
4. **30-week MA slope.** Clearly rising (the green line) for several weeks, not just turning up this week.
5. **Breakout volume.** The breakout week's volume bar is at least 2× the average (the dashboard's "Volume vs avg" row).
6. **How far price is from the 30-week MA.** If it's more than about 25% above, it's extended, so wait for a pullback instead of chasing.
7. **Clean overhead.** No big old resistance just above the current price (check the monthly chart for prior highs).
8. **Sector.** Other stocks in the same sector are also in Stage 2. The TraderLion guide says to prefer strong sectors.
9. **Data sanity.** No sudden 50%+ one-week gap. That's usually a split or bonus, not a real move.

Then follow the indicator's ENTER, ADD, HOLD and EXIT labels.

## 4. Known gaps

- screener.in uses **daily** data and the 200-day MA, while Weinstein uses the **weekly** 30-week MA. Some stocks will pass the screen but show Stage 1 or 3 in the indicator, and the reverse can happen too. The indicator decides.
- The 1-day MA slope is noisy, so the screen will include some stocks whose MA is really flat.
- There's no relative-strength-versus-Nifty filter, so compare stocks against each other with the return columns.

---

# Chartink scans (recommended for the technical screen)

Chartink works on **weekly candles**, so it can apply the v1 rules almost exactly. Create a scan at chartink.com → Screener → Create scan, then paste a scan into the editor.

> **Syntax note:** Chartink's text editor is strict. If a line shows an error, rebuild just that clause with the editor's dropdowns: timeframe **Weekly**, offset **N weeks ago**, and the indicator **SMA**. The logic stays the same.
> `{cash}` = all NSE cash-segment stocks.

## Scan 1: Broad Stage 2 (your watchlist)

```
( {cash} (
  weekly close > weekly sma( weekly close , 30 )
  and weekly sma( weekly close , 30 ) > 4 weeks ago weekly sma( weekly close , 30 )
  and 4 weeks ago weekly sma( weekly close , 30 ) > 8 weeks ago weekly sma( weekly close , 30 )
  and weekly close > weekly sma( weekly close , 10 )
  and weekly close < weekly sma( weekly close , 30 ) * 1.25
  and market cap > 500
  and weekly sma( weekly volume , 10 ) * weekly close > 50000000
) )
```

| Line | v1 rule it matches |
|---|---|
| Close above the 30-week SMA | Price above the Stage MA |
| 30-week SMA higher than 4 weeks ago, and higher 4 weeks ago than 8 weeks ago | MA rising for at least 8 weeks, so not just a one-week tick up (v1 uses a 4-week slope) |
| Close above the 10-week SMA | Healthy short-term trend (v1's ADD gate) |
| Close below 30-week SMA × 1.25 | Not overextended (optional; delete this line to see everything) |
| Market cap > ₹500 Cr, weekly turnover > ₹5 Cr | Liquidity |

## Scan 2: Fresh breakout (v1 **ENTER** this week)

```
( {cash} (
  weekly close > weekly sma( weekly close , 30 )
  and weekly sma( weekly close , 30 ) >= 4 weeks ago weekly sma( weekly close , 30 )
  and weekly close > 1 week ago weekly max( 10 , weekly high )
  and weekly volume > weekly sma( weekly volume , 30 ) * 2
  and 1 week ago weekly max( 10 , weekly high ) < 1 week ago weekly min( 10 , weekly low ) * 1.35
  and weekly close > weekly open
  and market cap > 500
) )
```

| Line | v1 rule it matches |
|---|---|
| Close above the 30-week SMA, and the SMA not falling | v1 allows a breakout while the MA is still flat, as at the end of a Stage 1 base |
| Close above the previous 10-week high | Breakout above the top of the base (`baseHigh`, 10 weeks) |
| Weekly volume > 2× the 30-week average | Breakout volume rule (2×) |
| Previous 10-week range < 35% | **Approximation** of "there was a base": price moved sideways rather than spiking |
| Green weekly candle | Strong close (not in v1; delete it if you want exactly the v1 rule) |

Run this one **every weekend, after Friday's close**. Each result is a candidate ENTER. Confirm it on TradingView, where the v1 indicator should show an "S2 start" or ENTER label that week.

## Scan 3: Pullback to the 10-week MA (v1 **ADD**, or a late **retest ENTER**)

```
( {cash} (
  weekly close > weekly sma( weekly close , 30 )
  and weekly sma( weekly close , 30 ) > 4 weeks ago weekly sma( weekly close , 30 )
  and weekly low <= weekly sma( weekly close , 10 ) * 1.03
  and weekly close > weekly sma( weekly close , 10 )
  and weekly close > weekly open
  and weekly volume < weekly sma( weekly volume , 30 )
  and market cap > 500
) )
```

This matches v1's pullback ADD rule: price dipped to within 3% of the 10-week MA, closed back above it as a green candle, on below-average volume. Use it to find ADD opportunities in stocks you already hold, or a lower-risk entry in Stage 2 stocks you missed.

## What Chartink still can't do (check it on TradingView)

1. **The full stage history.** Was it really Stage 1 before, and not a Stage 3 top resolving upward? Look at the indicator's background colours.
2. **Base quality.** Scan 2's 35% range is only a rough proxy. Look for a clean, months-long base.
3. **Breakout level for retests.** v1 measures the retest against the exact base high, while Scan 3 uses the 10-week MA instead.
4. **Your own position state.** Tranche count, spacing between adds, and whether the trade is in profit all depend on your trades. The indicator tracks them, and no scanner can.
5. **Sector strength and data errors** (split or bonus gaps), the same as in the screener.in checklist above.

## Scan 4: Combined Stage 2 breakout (Scan 1 + Scan 2 in one)

This is Scan 2's breakout rules plus Scan 1's quality filters. The MA rule uses Scan 2's "not falling" instead of Scan 1's "rising for 8 weeks". Requiring an 8-week rise would drop the earliest breakouts from a flat Stage 1 base, and those are the best v1 entries.

```
( {cash} (
  weekly close > weekly sma( weekly close , 30 )
  and weekly sma( weekly close , 30 ) >= 4 weeks ago weekly sma( weekly close , 30 )
  and weekly close > 1 week ago weekly max( 10 , weekly high )
  and weekly volume > weekly sma( weekly volume , 30 ) * 2
  and 1 week ago weekly max( 10 , weekly high ) < 1 week ago weekly min( 10 , weekly low ) * 1.35
  and weekly close > weekly sma( weekly close , 10 )
  and weekly close < weekly sma( weekly close , 30 ) * 1.25
  and weekly close > weekly open
  and market cap > 500
  and weekly sma( weekly volume , 10 ) * weekly close > 50000000
) )
```

The result is a short list of stocks breaking out into Stage 2 this week that are liquid and not overextended. Your Stage 2 watchlist (Scan 1) stays a separate saved scan, because a combined "either/or" scan would mix both groups without telling you which stock is a fresh breakout.
