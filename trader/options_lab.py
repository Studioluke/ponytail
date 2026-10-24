"""What if the swing setups were traded with call options instead of shares?

    python -m trader.options_lab [--cache daily.json] [--spread 0.08] [--iv 1.3]

There is no long options price history here (Alpaca's starts in 2024), so
this models it: every STRETCH trade from trader/patterns.py is replayed as a
long call priced with Black-Scholes at entry and exit. Implied volatility
is the 20-day realised volatility times IV_PREMIUM, recomputed at exit (so
the volatility crush after a dip recovers is included), plus SPREAD of the
premium lost on each side. It is a model, not real fills; real spreads on
thin strikes are wider (retail averaged 12.6% in Bryzgalova et al. 2023).

Contracts compared, all bought with the same $200 premium a trade:
    shares          the baseline
    call 35d 0.70   in the money, about 35 days to expiry (less time decay)
    call 35d ATM    at the money, 35 days
    call 7d ATM     weekly at the money, what retail mostly buys
"""
import json
import sys
from math import erf, exp, log, sqrt
from statistics import mean, pstdev

from . import patterns as P

R_FREE = 0.04
IV_PREMIUM = 1.15
SPREAD = 0.03
CONTRACTS = {"call 35d 0.70 delta": (35, 0.70), "call 35d ATM": (35, 0.50), "call 7d ATM": (7, 0.50)}


def _n(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def bs_call(s, k, t, vol, r=R_FREE):
    if t <= 0:
        return max(s - k, 0.0)
    d1 = (log(s / k) + (r + vol * vol / 2) * t) / (vol * sqrt(t))
    return s * _n(d1) - k * exp(-r * t) * _n(d1 - vol * sqrt(t))


def strike_for_delta(s, t, vol, delta, r=R_FREE):
    """Invert N(d1) = delta for the strike."""
    lo, hi = 0.3 * s, 2.0 * s
    for _ in range(60):
        k = (lo + hi) / 2
        d1 = (log(s / k) + (r + vol * vol / 2) * t) / (vol * sqrt(t))
        lo, hi = (k, hi) if _n(d1) > delta else (lo, k)
    return (lo + hi) / 2


def realised_vol(closes, i, n=20):
    rets = [log(closes[j] / closes[j - 1]) for j in range(i - n + 1, i + 1)]
    return max(pstdev(rets) * sqrt(252), 0.10)


def replay(bars_by_symbol, rule=None):
    rule = rule or "STRETCH: close < 10d avg - 2 ATR, IBS<0.25, above 200d, exit >5d avg"
    entry, exit_fn, hold, stop = P.RULES[rule]
    rows = {"shares": []} | {c: [] for c in CONTRACTS}
    for bars in bars_by_symbol.values():
        if len(bars) < 260:
            continue
        idx = {b["t"][:10]: n for n, b in enumerate(bars)}
        closes = [b["c"] for b in bars]
        for t in P.run_rule(bars, entry, exit_fn, hold, stop):
            i = idx[t["day"]]
            j = min(i + t["days"], len(bars) - 1)
            s0, s1 = closes[i], closes[j]
            v0, v1 = realised_vol(closes, i) * IV_PREMIUM, realised_vol(closes, j) * IV_PREMIUM
            rows["shares"].append({"day": t["day"], "ret": t["ret"]})
            for name, (dte, delta) in CONTRACTS.items():
                k = strike_for_delta(s0, dte / 365, v0, delta)
                p0 = bs_call(s0, k, dte / 365, v0) * (1 + SPREAD)
                cal = (j - i) * 7 / 5  # trading days to calendar days
                p1 = bs_call(s1, k, max(dte - cal, 0) / 365, v1) * (1 - SPREAD)
                rows[name].append({"day": t["day"], "ret": p1 / p0 - 1})
    return rows


def main(argv):
    global SPREAD, IV_PREMIUM
    cache = argv[argv.index("--cache") + 1] if "--cache" in argv else None
    if "--spread" in argv:
        SPREAD = float(argv[argv.index("--spread") + 1])
    if "--iv" in argv:
        IV_PREMIUM = float(argv[argv.index("--iv") + 1])
    print(f"Spread {SPREAD:.0%} a side, implied vol = {IV_PREMIUM:.2f} x realised\n")
    bars = P.load(cache)
    rows = replay(bars)
    print("| Instrument | Trades | Win % | Avg return on money put in | Profit factor | Worst trade | $ per trade at $200 |")
    print("|---|---|---|---|---|---|---|")
    for name, trades in rows.items():
        s = P.stats(trades)
        worst = min(t["ret"] for t in trades)
        print(f"| {name} | {s['n']} | {s['win']:.0%} | {s['avg']:+.1%} | {s['pf']:.2f} | {worst:.0%} | ${200 * s['avg']:+.2f} |")


if __name__ == "__main__":
    main(sys.argv[1:])
