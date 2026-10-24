"""Pattern lab: candlestick, chart-pattern and indicator rules, tested on daily bars.

Every rule from the research note (trader/journal/notes/trading-playbook.md)
is written here as code and replayed on Alpaca daily bars, so the playbook
rests on our own numbers rather than on articles.

    python -m trader.patterns                 # all rules, 36 symbols, 2016-now
    python -m trader.patterns --cache FILE    # reuse a saved bars JSON

Fills: a signal on day t's close buys at that close (a market-on-close order
placed a few minutes before 4pm). Exits are checked from day t+1: an
optional stop (low <= stop exits at the stop, or the open if it gapped
through), then the rule's own exit at the close, then a time stop. Costs:
COST per side as a fraction of price (default 0.05%). Long only.

Each rule is judged by trade count, win rate, average trade, profit factor
and expectancy, separately for 2016-2021 (in-sample) and 2022-now
(out-of-sample), and against a baseline of buying any day in the same
trend regime and holding the same number of days. A rule only earns a
place in the playbook if it beats that baseline in both periods.
"""
import json
import sys
from statistics import mean

COST = 0.0005
SPLIT = "2022-01-01"

SYMBOLS = ("SPY,QQQ,IWM,DIA,AAPL,MSFT,GOOGL,NVDA,META,AMZN,TSLA,AMD,NFLX,AVGO,COST,JPM,XOM,UNH,V,HD,"
           "PG,KO,CRM,ORCL,ADBE,PANW,CRWD,FTNT,LLY,WMT,XLF,XLE,XLK,SMH,GLD,TLT").split(",")


# ---------- indicators (lists aligned with the bars; None until warm) ----------

def sma(xs, n):
    out, s = [None] * len(xs), 0.0
    for i, x in enumerate(xs):
        s += x
        if i >= n:
            s -= xs[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def rsi(closes, n):
    """Wilder RSI."""
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag, al = mean(gains[:n]), mean(losses[:n])
    for i in range(n, len(closes)):
        if i > n:
            ag = (ag * (n - 1) + gains[i - 1]) / n
            al = (al * (n - 1) + losses[i - 1]) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def atr(bars, n=14):
    trs = [bars[0]["h"] - bars[0]["l"]] + [
        max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])) for p, b in zip(bars, bars[1:])]
    return sma(trs, n)


def ibs(b):
    """Internal bar strength: where the close sits in the day's range, 0 = low, 1 = high."""
    r = b["h"] - b["l"]
    return (b["c"] - b["l"]) / r if r else 0.5


# ---------- candle anatomy ----------

def body(b):
    return abs(b["c"] - b["o"])


def upper_wick(b):
    return b["h"] - max(b["o"], b["c"])


def lower_wick(b):
    return min(b["o"], b["c"]) - b["l"]


def rng(b):
    return b["h"] - b["l"]


def is_hammer(b):
    """Long lower wick (whisker) at least twice the body, small upper wick, close in the top third."""
    r = rng(b)
    return r > 0 and lower_wick(b) >= 2 * max(body(b), 0.001 * b["c"]) and upper_wick(b) <= 0.25 * r \
        and (b["c"] - b["l"]) / r >= 2 / 3


def is_bull_engulfing(p, b):
    return p["c"] < p["o"] and b["c"] > b["o"] and b["o"] <= p["c"] and b["c"] >= p["o"] and body(b) > body(p)


def is_morning_star(a, m, b):
    """Big down candle, small middle candle, big up candle closing past the first one's midpoint."""
    return a["c"] < a["o"] and body(a) >= 0.6 * rng(a) and body(m) <= 0.3 * max(rng(m), 1e-9) \
        and b["c"] > b["o"] and b["c"] >= (a["o"] + a["c"]) / 2


def is_three_white_soldiers(a, m, b):
    up = all(x["c"] > x["o"] and body(x) >= 0.6 * max(rng(x), 1e-9) for x in (a, m, b))
    return up and a["c"] < m["c"] < b["c"] and a["o"] < m["o"] <= a["c"] and m["o"] < b["o"] <= m["c"]


def is_bull_harami(p, b):
    return p["c"] < p["o"] and body(p) >= 0.6 * rng(p) and b["c"] > b["o"] and b["o"] > p["c"] and b["c"] < p["o"]


def is_doji(b):
    return rng(b) > 0 and body(b) <= 0.1 * rng(b)


# ---------- rules ----------
# A rule maps (context, i) -> a dict with an optional "stop" (price) or None.
# Exit functions map (context, i_entry, j) -> True to sell at day j's close.

class Ctx:
    def __init__(self, bars):
        self.b = bars
        self.c = [x["c"] for x in bars]
        self.sma5, self.sma10, self.sma20 = sma(self.c, 5), sma(self.c, 10), sma(self.c, 20)
        self.sma50, self.sma200 = sma(self.c, 50), sma(self.c, 200)
        self.rsi2, self.rsi14 = rsi(self.c, 2), rsi(self.c, 14)
        self.atr = atr(bars)
        self.vol20 = sma([x["v"] for x in bars], 20)

    def uptrend(self, i):
        return self.sma200[i] is not None and self.c[i] > self.sma200[i]

    def down_days(self, i, k):
        return i >= k and all(self.c[i - j] < self.c[i - j - 1] for j in range(k))

    def pulled_back(self, i, k=5):
        """Close below where it was k days ago (a short decline before a reversal candle)."""
        return i >= k and self.c[i] < self.c[i - k]


def exit_above_sma5(x, i, j):
    return x.c[j] > x.sma5[j]


def exit_above_prev_high(x, i, j):
    return x.c[j] > x.b[j - 1]["h"]


def exit_rsi2_above_70(x, i, j):
    return x.rsi2[j] is not None and x.rsi2[j] > 70


def exit_below_sma10(x, i, j):
    return x.c[j] < x.sma10[j]


def exit_never(x, i, j):
    return False


def _atr_stop(x, i, k):
    return x.c[i] - k * x.atr[i] if x.atr[i] else None


RULES = {
    # Mean reversion in an uptrend (Connors and the IBS literature).
    "RSI2<10 above 200d, exit >5d avg":
        (lambda x, i: x.uptrend(i) and x.rsi2[i] < 10, exit_above_sma5, 10, None),
    "RSI2<5 above 200d, exit >5d avg":
        (lambda x, i: x.uptrend(i) and x.rsi2[i] < 5, exit_above_sma5, 10, None),
    "RSI2<10 above 200d, exit >5d avg, 2.5 ATR stop":
        (lambda x, i: x.uptrend(i) and x.rsi2[i] < 10, exit_above_sma5, 10, 2.5),
    # Confluence: a stretch below the 10d average that also closes near the day's low (long lower
    # whisker not yet formed). These are the playbook's core swing setups.
    "STRETCH: close < 10d avg - 2 ATR, IBS<0.25, above 200d, exit >5d avg":
        (lambda x, i: stretch(x, i), exit_above_sma5, 10, None),
    "RSI2<5 + IBS<0.2 above 200d, exit > prior high":
        (lambda x, i: x.uptrend(i) and x.rsi2[i] < 5 and ibs(x.b[i]) < 0.2, exit_above_prev_high, 10, None),
    "IBS<0.2 above 200d, exit > prior high":
        (lambda x, i: x.uptrend(i) and ibs(x.b[i]) < 0.2, exit_above_prev_high, 5, None),
    "IBS<0.2 + RSI2<10 above 200d":
        (lambda x, i: x.uptrend(i) and ibs(x.b[i]) < 0.2 and x.rsi2[i] < 10, exit_above_prev_high, 5, None),
    "3 down closes above 200d, exit >5d avg":
        (lambda x, i: x.uptrend(i) and x.down_days(i, 3), exit_above_sma5, 10, None),
    "Close below lower 2.5-ATR band of 10d avg, above 200d":
        (lambda x, i: x.uptrend(i) and x.c[i] < x.sma10[i] - 2.5 * x.atr[i], exit_above_sma5, 10, None),
    # Candlesticks, judged as the classic books say: a reversal after a pullback, in an uptrend.
    "Hammer after pullback, above 200d, hold 5d":
        (lambda x, i: x.uptrend(i) and x.pulled_back(i) and is_hammer(x.b[i]), exit_never, 5, None),
    "Hammer after pullback, above 200d, exit >5d avg":
        (lambda x, i: x.uptrend(i) and x.pulled_back(i) and is_hammer(x.b[i]), exit_above_sma5, 10, None),
    "Hammer anywhere, hold 5d":
        (lambda x, i: is_hammer(x.b[i]), exit_never, 5, None),
    "Bullish engulfing after pullback, above 200d, hold 5d":
        (lambda x, i: x.uptrend(i) and x.pulled_back(i) and is_bull_engulfing(x.b[i - 1], x.b[i]), exit_never, 5, None),
    "Bullish engulfing anywhere, hold 5d":
        (lambda x, i: is_bull_engulfing(x.b[i - 1], x.b[i]), exit_never, 5, None),
    "Morning star after pullback, hold 5d":
        (lambda x, i: x.pulled_back(i - 1) and is_morning_star(x.b[i - 2], x.b[i - 1], x.b[i]), exit_never, 5, None),
    "Bullish harami after pullback, above 200d, hold 5d":
        (lambda x, i: x.uptrend(i) and x.pulled_back(i - 1) and is_bull_harami(x.b[i - 1], x.b[i]), exit_never, 5, None),
    "Three white soldiers, hold 10d":
        (lambda x, i: is_three_white_soldiers(x.b[i - 2], x.b[i - 1], x.b[i]), exit_never, 10, None),
    "Doji after 3 down days, above 200d, hold 5d":
        (lambda x, i: x.uptrend(i) and x.down_days(i - 1, 3) and is_doji(x.b[i]), exit_never, 5, None),
    # Momentum / breakout (Donchian, volume confirmation, 52-week highs).
    "20d high breakout on 1.5x volume, trail 10d avg":
        (lambda x, i: x.uptrend(i) and x.c[i] > max(x.b[k]["h"] for k in range(i - 20, i))
         and x.b[i]["v"] > 1.5 * x.vol20[i - 1], exit_below_sma10, 40, 2.0),
    "20d high breakout, trail 10d avg":
        (lambda x, i: x.uptrend(i) and x.c[i] > max(x.b[k]["h"] for k in range(i - 20, i)), exit_below_sma10, 40, 2.0),
    "52-week high close, trail 10d avg":
        (lambda x, i: i >= 252 and x.c[i] >= max(x.c[i - 252:i]), exit_below_sma10, 40, 2.0),
    "Pullback to 20d avg in 50>200 uptrend, exit RSI2>70":
        (lambda x, i: x.sma50[i] and x.sma50[i] > x.sma200[i] and x.b[i]["l"] <= x.sma20[i] < x.c[i]
         and x.c[i - 1] > x.sma20[i - 1], exit_rsi2_above_70, 10, 2.0),
    "Golden cross (50d over 200d), trail 50d avg":
        (lambda x, i: x.sma200[i - 1] and x.sma50[i - 1] <= x.sma200[i - 1] and x.sma50[i] > x.sma200[i],
         lambda x, i, j: x.c[j] < x.sma50[j] * 0.97, 250, None),
    "Inside day (NR) breakout above 50d, hold 5d":
        (lambda x, i: x.sma50[i] and x.c[i] > x.sma50[i] and x.b[i - 1]["h"] < x.b[i - 2]["h"]
         and x.b[i - 1]["l"] > x.b[i - 2]["l"] and x.c[i] > x.b[i - 1]["h"], exit_never, 5, 1.5),
    # Oscillator classics.
    "RSI14 crosses up through 30, hold 10d":
        (lambda x, i: x.rsi14[i - 1] is not None and x.rsi14[i - 1] < 30 <= x.rsi14[i], exit_never, 10, None),
    "Double bottom (two 20d lows within 2%, close > middle peak)":
        (lambda x, i: _double_bottom(x, i), exit_below_sma10, 30, 1.5),
}


def stretch(x, i):
    return x.uptrend(i) and x.atr[i] is not None and x.c[i] < x.sma10[i] - 2.0 * x.atr[i] and ibs(x.b[i]) < 0.25


def _double_bottom(x, i, look=40):
    """Two swing lows within 2% of each other at least 8 days apart, and today closes above the peak between them."""
    if i < look + 2:
        return False
    w = x.b[i - look:i]
    lows = [k for k in range(2, len(w) - 2) if w[k]["l"] == min(b["l"] for b in w[k - 2:k + 3])]
    for a in range(len(lows)):
        for c in range(a + 1, len(lows)):
            l1, l2 = w[lows[a]]["l"], w[lows[c]]["l"]
            if lows[c] - lows[a] >= 8 and abs(l1 - l2) / l1 <= 0.02:
                peak = max(b["h"] for b in w[lows[a]:lows[c] + 1])
                if peak > 1.04 * min(l1, l2) and x.c[i] > peak and x.c[i - 1] <= peak:
                    return True
    return False


# ---------- engine ----------

def run_rule(bars, entry, exit_fn, max_hold, stop_atr, cost=COST):
    x, trades, i = Ctx(bars), [], 205
    while i < len(bars) - 1:
        try:
            hit = x.sma200[i] is not None and entry(x, i)
        except (TypeError, IndexError):
            hit = False
        if not hit:
            i += 1
            continue
        px = x.c[i] * (1 + cost)
        stop = _atr_stop(x, i, stop_atr) if stop_atr else None
        out, how, j = None, "time", i
        for j in range(i + 1, min(i + 1 + max_hold, len(bars))):
            b = bars[j]
            if stop and b["l"] <= stop:
                out, how = min(stop, b["o"]), "stop"
                break
            if exit_fn(x, i, j):
                out, how = b["c"], "rule"
                break
        if out is None:
            out = bars[j]["c"]
        out *= (1 - cost)
        trades.append({"day": bars[i]["t"][:10], "ret": out / px - 1, "days": j - i, "how": how})
        i = j + 1  # one position per symbol at a time
    return trades


def baseline(bars, max_hold):
    """Buy every day above the 200d average and hold max_hold days: what drift alone pays."""
    x, out = Ctx(bars), []
    for i in range(205, len(bars) - max_hold):
        if x.uptrend(i):
            out.append({"day": bars[i]["t"][:10], "ret": x.c[i + max_hold] / x.c[i] - 1 - 2 * COST})
    return out


def stats(trades):
    n = len(trades)
    if not n:
        return {"n": 0}
    rets = [t["ret"] for t in trades]
    wins = [r for r in rets if r > 0]
    gl = -sum(r for r in rets if r < 0)
    return {"n": n, "win": len(wins) / n, "avg": mean(rets),
            "pf": (sum(wins) / gl) if gl else float("inf"),
            "avg_win": mean(wins) if wins else 0.0,
            "avg_loss": mean([r for r in rets if r <= 0]) if n > len(wins) else 0.0,
            "days": mean(t.get("days", 0) for t in trades)}


def evaluate(bars_by_symbol, rules=RULES):
    rows = []
    for name, (entry, exit_fn, hold, stop) in rules.items():
        series = [bs for bs in bars_by_symbol.values() if len(bs) >= 260]
        trades = [t for bs in series for t in run_rule(bs, entry, exit_fn, hold, stop)]
        held = max(1, round(mean(t["days"] for t in trades))) if trades else hold
        base = [t for bs in series for t in baseline(bs, held)]
        ins = [t for t in trades if t["day"] < SPLIT]
        oos = [t for t in trades if t["day"] >= SPLIT]
        b_in = stats([t for t in base if t["day"] < SPLIT])
        b_out = stats([t for t in base if t["day"] >= SPLIT])
        rows.append({"rule": name, "all": stats(trades), "in": stats(ins), "out": stats(oos),
                     "base_in": b_in, "base_out": b_out})
    return rows


def verdict(r):
    i, o = r["in"], r["out"]
    if i.get("n", 0) < 30 or o.get("n", 0) < 30:
        return "too few trades"
    edge_in = i["avg"] - r["base_in"]["avg"]
    edge_out = o["avg"] - r["base_out"]["avg"]
    if i["pf"] > 1.2 and o["pf"] > 1.2 and edge_in > 0 and edge_out > 0:
        return "KEEP"
    if i["pf"] > 1 and o["pf"] > 1 and (edge_in > 0 or edge_out > 0):
        return "weak"
    return "drop"


def table(rows):
    lines = ["| Rule | Trades | Win % | Avg trade | Profit factor | Avg days | 2016-21 win / PF | 2022-26 win / PF | Edge vs baseline (in / out) | Verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -(r["all"].get("pf", 0) if r["all"].get("n") else 0)):
        a, i, o = r["all"], r["in"], r["out"]
        if not a.get("n"):
            lines.append(f"| {r['rule']} | 0 | | | | | | | | no trades |")
            continue
        e_in = (i.get("avg", 0) - r["base_in"].get("avg", 0)) * 100
        e_out = (o.get("avg", 0) - r["base_out"].get("avg", 0)) * 100
        lines.append(
            f"| {r['rule']} | {a['n']} | {a['win']:.0%} | {a['avg']:+.2%} | {a['pf']:.2f} | {a['days']:.1f} | "
            f"{i.get('win', 0):.0%} / {i.get('pf', 0):.2f} | {o.get('win', 0):.0%} / {o.get('pf', 0):.2f} | "
            f"{e_in:+.2f}% / {e_out:+.2f}% | {verdict(r)} |")
    return "\n".join(lines)


def portfolio(bars_by_symbol, rule, cash=1000.0, position=200.0, max_open=5):
    """Replay one rule across all symbols with a shared account: fixed dollars per trade,
    at most max_open at once, earliest signals first. Returns yearly P&L and max drawdown."""
    entry, exit_fn, hold, stop = RULES[rule]
    trades = []
    for sym, bars in bars_by_symbol.items():
        if len(bars) >= 260:
            for t in run_rule(bars, entry, exit_fn, hold, stop):
                k = next(n for n, b in enumerate(bars) if b["t"][:10] == t["day"])
                t.update(sym=sym, out=bars[min(k + t["days"], len(bars) - 1)]["t"][:10])
                trades.append(t)
    trades.sort(key=lambda t: t["day"])
    taken, open_, eq, peak, dd, years = [], [], cash, cash, 0.0, {}
    for t in trades:
        open_ = [o for o in open_ if o["out"] > t["day"]]
        if len(open_) >= max_open:
            continue
        open_.append(t)
        pnl = position * t["ret"]
        eq += pnl
        peak, dd = max(peak, eq), min(dd, eq - peak)
        years[t["day"][:4]] = years.get(t["day"][:4], 0.0) + pnl
        taken.append(t)
    return {"trades": len(taken), "win": stats(taken).get("win", 0), "end": eq, "max_dd": dd, "years": years}


def load(cache=None, start="2016-01-01", end=None):
    if cache:
        with open(cache) as f:
            return json.load(f)
    from .broker import Broker
    return Broker().bars(list(SYMBOLS), "1Day", start, end, feed="sip", adjustment="all")


def main(argv):
    cache = argv[argv.index("--cache") + 1] if "--cache" in argv else None
    bars = load(cache)
    print(table(evaluate(bars)))
    for rule in ("STRETCH: close < 10d avg - 2 ATR, IBS<0.25, above 200d, exit >5d avg",
                 "RSI2<5 + IBS<0.2 above 200d, exit > prior high"):
        p = portfolio(bars, rule)
        yrs = ", ".join(f"{y} ${v:+.0f}" for y, v in sorted(p["years"].items()))
        print(f"\n{rule}: $1,000 account, $200 a trade, max 5 open -> {p['trades']} trades, "
              f"{p['win']:.0%} won, ends ${p['end']:,.0f}, worst drawdown ${p['max_dd']:.0f}\n  {yrs}")


if __name__ == "__main__":
    main(sys.argv[1:])
