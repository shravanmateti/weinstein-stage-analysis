"""Draws charts/trade_return_histogram.png from results/backtest_trades.csv.
Run from anywhere: python3 charts/make_histogram.py
"""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parent.parent
d = pd.read_csv(ROOT / 'results' / 'backtest_trades.csv')
r = d[d.status == 'exit'].return_pct
SURF, INK, INK2, GRID, LOSS, WIN = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#e34948', '#2a78d6'
LO, HI, W = -50, 200, 5
edges = np.arange(LO, HI + W, W)
counts = pd.cut(r[(r > LO) & (r <= HI)], edges, right=True).value_counts().sort_index().to_numpy()
under, over = (r <= LO).sum(), (r > HI).sum()
fig, ax = plt.subplots(figsize=(12, 6.2), dpi=160, facecolor=SURF); ax.set_facecolor(SURF)
lefts = edges[:-1]
ax.bar(lefts, counts, width=W, align='edge', color=[LOSS if e < 0 else WIN for e in lefts], edgecolor=SURF, linewidth=1.5)
# overflow bars
ax.bar(LO - 2 * W, under, width=W, align='edge', color=LOSS, edgecolor=SURF, linewidth=1.5, hatch='////', alpha=.85)
ax.bar(HI + W, over, width=W, align='edge', color=WIN, edgecolor=SURF, linewidth=1.5, hatch='////', alpha=.85)
ax.text(LO - 1.5 * W, under + 12, f'≤{LO}%\n{under}', ha='center', va='bottom', fontsize=9, color=INK2)
ax.text(HI + 1.5 * W, over + 12, f'>{HI}%\n{over}\n(max +{r.max():.0f}%)', ha='center', va='bottom', fontsize=9, color=INK2)
for x, lab, dy, ha, dx in [(r.median(), f'Median {r.median():.1f}%', 0.97, 'right', -1.5), (r.mean(), f'Average +{r.mean():.1f}%', 0.97, 'left', 1.5)]:
    ax.axvline(x, color=INK, lw=1.2, ls=(0, (4, 3)))
    ax.text(x + dx, ax.get_ylim()[1] * dy, lab, fontsize=10, color=INK, va='top', ha=ha, bbox=dict(fc=SURF, ec='none', pad=1))
wins, losses = (r > 0).sum(), (r <= 0).sum()
ax.text(-45, max(counts) * 0.60, f'Losses (≤0%)\n{losses} trades · {losses/len(r)*100:.0f}%\navg {r[r<=0].mean():.1f}%', color=LOSS, fontsize=11, fontweight='bold')
ax.text(60, max(counts) * 0.45, f'Wins (>0%)\n{wins} trades · {wins/len(r)*100:.0f}%\navg +{r[r>0].mean():.1f}%', color=WIN, fontsize=11, fontweight='bold')
ax.set_xlim(LO - 2.5 * W, HI + 2.5 * W)
ax.set_xticks(list(range(LO, HI + 1, 25))); ax.set_xticklabels([f'{t:+d}%' if t else '0%' for t in range(LO, HI + 1, 25)])
ax.set_xlabel('Return per trade (5% buckets)', color=INK2); ax.set_ylabel('Number of trades', color=INK2)
ax.tick_params(colors=INK2, length=0); ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID)
fig.suptitle('Most trades are small losses; a long tail of big winners pays for them', x=0.06, ha='left', fontsize=14, fontweight='bold', color=INK)
ax.set_title(f'v1 rules, {len(r)} closed trades, 594 NSE Stage 2 stocks, 2016–2026 (weekly)', loc='left', fontsize=10, color=INK2, pad=10)
fig.tight_layout(); fig.savefig(ROOT / 'charts' / 'trade_return_histogram.png', facecolor=SURF)
print('Saved', ROOT / 'charts' / 'trade_return_histogram.png')
