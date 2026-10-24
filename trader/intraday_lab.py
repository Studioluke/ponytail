"""Day-trading pattern lab on 5-minute bars (long only, flat by 15:55 ET).

    python -m trader.intraday_lab DIR      # DIR holds m5_<SYMBOL>.json bar files
    python -m trader.intraday_lab          # fetches 2024-now from Alpaca (slow, rate-limited)

Each rule sees only completed 5-minute bars. An entry fills at the signal
bar's close plus COST; a stop fills at the stop (or the bar's open if it
gapped through), a target at the target; when a bar touches both, the stop
counts. Anything still open at 15:55 sells at that bar's open. Results are
split into 2024 (in-sample) and 2025-now (out-of-sample), and reported in
R (multiples of the risk taken) as well as percent, since a day trade's
quality is its reward against its stop.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, time
from statistics import mean
from zoneinfo import ZoneInfo

from .patterns import ibs, is_hammer, rsi, sma

ET = ZoneInfo("America/New_York")
COST = 0.0002
SPLIT = "2025-01-01"
SYMBOLS = "SPY,QQQ,IWM,AAPL,MSFT,GOOGL,NVDA,META,AMZN,TSLA,AMD,NFLX,AVGO,COST,PANW,CRWD".split(",")
FLAT = time(15, 55)


def sessions(bars):
    days = defaultdict(list)
    for b in bars:
        t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
        if time(9, 30) <= t.time() < time(16, 0):
            days[t.date().isoformat()].append(dict(b, et=t.time()))
    return dict(sorted(days.items()))


def vwap_series(day):
    out, pv, vol = [], 0.0, 0.0
    for b in day:
        pv += (b["h"] + b["l"] + b["c"]) / 3 * b["v"]
        vol += b["v"]
        out.append(pv / vol if vol else b["c"])
    return out


def walk(day, i, entry, stop, target=None, exit_fn=None):
    """Follow a long from bar i's close. Returns (exit price, how)."""
    for j in range(i + 1, len(day)):
        b = day[j]
        if b["et"] >= FLAT:
            return b["o"], "close"
        if b["l"] <= stop:
            return min(stop, b["o"]), "stop"
        if target and b["h"] >= target:
            return max(target, b["o"]), "target"
        if exit_fn and exit_fn(j):
            return b["c"], "rule"
    return day[-1]["c"], "close"


# Each rule: f(day, ctx) -> list of trades (entry, stop, exit, how). ctx carries the
# prior days' context: prev_close, daily uptrend flag, first-bar relative volume.

def r_orb5(day, ctx, rvol_min=0.0):
    f = day[0]
    if f["c"] <= f["o"] or ctx["rvol"] < rvol_min or len(day) < 3:
        return []
    entry, stop = f["c"], f["l"]
    if entry - stop < 0.0005 * entry:
        return []
    px, how = walk(day, 0, entry, stop, entry + 10 * (entry - stop))
    return [(entry, stop, px, how)]


def r_orb15_vwap(day, ctx):
    if len(day) < 4:
        return []
    hi, lo = max(b["h"] for b in day[:3]), min(b["l"] for b in day[:3])
    vw = vwap_series(day)
    for i in range(3, len(day)):
        if day[i]["et"] >= time(15, 30):
            return []
        if day[i]["c"] > hi and day[i]["c"] > vw[i]:
            entry, stop = day[i]["c"], (hi + lo) / 2
            px, how = walk(day, i, entry, stop, entry + 2 * (entry - stop))
            return [(entry, stop, px, how)]
    return []


def r_vwap_trend(day, ctx):
    """Zarattini & Aziz (2023), long side: hold while 5-min closes stay above VWAP."""
    vw, trades, i = vwap_series(day), [], 0
    while i < len(day) - 1:
        b = day[i]
        if b["et"] >= time(15, 30):
            break
        if b["c"] > vw[i] and (i == 0 or day[i - 1]["c"] <= vw[i - 1]):
            entry, stop = b["c"], min(b["l"], vw[i]) - 0.001 * b["c"]
            px, how, j = None, "close", i
            for j in range(i + 1, len(day)):
                if day[j]["et"] >= FLAT:
                    px = day[j]["o"]
                    break
                if day[j]["l"] <= stop:
                    px, how = min(stop, day[j]["o"]), "stop"
                    break
                if day[j]["c"] < vw[j]:
                    px, how = day[j]["c"], "rule"
                    break
            trades.append((entry, stop, px if px is not None else day[-1]["c"], how))
            i = j + 1
        else:
            i += 1
    return trades


def r_gap_fill(day, ctx):
    """Gap down 0.5-3% in a daily uptrend, first bar closes green: buy, target the prior close."""
    pc = ctx["prev_close"]
    gap = day[0]["o"] / pc - 1
    if not ctx["uptrend"] or not -0.03 <= gap <= -0.005 or day[0]["c"] <= day[0]["o"]:
        return []
    entry, stop = day[0]["c"], day[0]["l"]
    if entry >= pc or entry - stop <= 0:
        return []
    px, how = walk(day, 0, entry, stop, pc)
    return [(entry, stop, px, how)]


def r_meanrev(day, ctx):
    """5-min RSI(2)<5 and IBS<0.2 in a daily uptrend: buy the flush, sell the first close above the prior high."""
    if not ctx["uptrend"]:
        return []
    closes = [b["c"] for b in day]
    r2 = rsi(closes, 2)
    rngs = sma([b["h"] - b["l"] for b in day], 6)
    trades, i = [], 6
    while i < len(day) - 1:
        b = day[i]
        if b["et"] >= time(15, 0):
            break
        if r2[i] is not None and r2[i] < 5 and ibs(b) < 0.2 and rngs[i]:
            entry, stop = b["c"], b["c"] - 3 * rngs[i]
            px, how, j = None, "close", i
            for j in range(i + 1, len(day)):
                if day[j]["et"] >= FLAT:
                    px = day[j]["o"]
                    break
                if day[j]["l"] <= stop:
                    px, how = min(stop, day[j]["o"]), "stop"
                    break
                if day[j]["c"] > day[j - 1]["h"]:
                    px, how = day[j]["c"], "rule"
                    break
            trades.append((entry, stop, px if px is not None else day[-1]["c"], how))
            i = j + 1
        else:
            i += 1
    return trades


def r_hammer_vwap(day, ctx):
    """A 5-min hammer whose lower wick tags VWAP after three closes above it: buy, stop under the wick, 2R."""
    vw = vwap_series(day)
    for i in range(4, len(day) - 1):
        b = day[i]
        if b["et"] >= time(15, 0):
            return []
        if all(day[k]["c"] > vw[k] for k in range(i - 3, i)) and b["l"] <= vw[i] < b["c"] and is_hammer(b):
            entry, stop = b["c"], b["l"] - 0.0005 * b["c"]
            px, how = walk(day, i, entry, stop, entry + 2 * (entry - stop))
            return [(entry, stop, px, how)]
    return []


def r_bull_flag(day, ctx):
    """Up 1%+ from the open by 10:00 (the pole), a 2-6 bar pullback that holds VWAP and gives back
    under half the pole (the flag), then a close above the flag's high. Stop under the flag, 2R."""
    if len(day) < 12:
        return []
    vw, o = vwap_series(day), day[0]["o"]
    pole_end = max(range(6), key=lambda k: day[k]["h"])
    top = day[pole_end]["h"]
    if top / o - 1 < 0.01:
        return []
    for i in range(pole_end + 3, min(pole_end + 8, len(day) - 1)):
        flag = day[pole_end + 1:i]
        if not 2 <= len(flag) <= 6:
            continue
        low = min(b["l"] for b in flag)
        if low < top - 0.5 * (top - o) or any(b["c"] < vw[pole_end + 1 + k] for k, b in enumerate(flag)):
            return []
        if day[i]["c"] > max(b["h"] for b in flag):
            entry, stop = day[i]["c"], low - 0.0005 * low
            px, how = walk(day, i, entry, stop, entry + 2 * (entry - stop))
            return [(entry, stop, px, how)]
    return []


RULES = {
    "ORB 5-min, first bar green, stop its low, 10R or close": r_orb5,
    "ORB 5-min, stocks in play (first bar 2x usual volume)": lambda d, c: r_orb5(d, c, 2.0),
    "ORB 15-min + VWAP, stop midpoint, 2R (current bot)": r_orb15_vwap,
    "VWAP trend: long above VWAP, out on a close below": r_vwap_trend,
    "Gap-down fill in uptrend, target prior close": r_gap_fill,
    "5-min RSI2<5 + IBS<0.2 flush in uptrend": r_meanrev,
    "Hammer tagging VWAP, 2R": r_hammer_vwap,
    "Bull flag after 1% morning pole, 2R": r_bull_flag,
}


def contexts(days):
    keys, out = list(days), {}
    closes = [days[k][-1]["c"] for k in keys]
    s20 = sma(closes, 20)
    first_vol = [days[k][0]["v"] for k in keys]
    for n, k in enumerate(keys):
        if n < 20:
            continue
        out[k] = {"prev_close": closes[n - 1], "uptrend": s20[n - 1] is not None and closes[n - 1] > s20[n - 1],
                  "rvol": first_vol[n] / (mean(first_vol[n - 14:n]) or 1)}
    return out


def evaluate(bars_by_symbol):
    res = {name: [] for name in RULES}
    for sym, bars in bars_by_symbol.items():
        days = sessions(bars)
        ctx = contexts(days)
        for d, day in days.items():
            if d not in ctx:
                continue
            for name, fn in RULES.items():
                for entry, stop, px, how in fn(day, ctx[d]):
                    e, x = entry * (1 + COST), px * (1 - COST)
                    res[name].append({"day": d, "sym": sym, "ret": x / e - 1, "r": (x - e) / (entry - stop), "how": how})
    return res


def _s(ts):
    n = len(ts)
    if not n:
        return None
    wins = [t for t in ts if t["ret"] > 0]
    gl = -sum(t["ret"] for t in ts if t["ret"] < 0)
    return {"n": n, "win": len(wins) / n, "r": mean(t["r"] for t in ts), "avg": mean(t["ret"] for t in ts),
            "pf": sum(t["ret"] for t in wins) / gl if gl else float("inf")}


def table(res):
    lines = ["| Rule | Trades | Win % | Avg R | Avg trade | Profit factor | 2024 win / PF | 2025-26 win / PF | Verdict |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, ts in sorted(res.items(), key=lambda kv: -(_s(kv[1]) or {"pf": 0})["pf"]):
        none = {"n": 0, "win": 0, "pf": 0}
        a = _s(ts)
        i = _s([t for t in ts if t["day"] < SPLIT]) or none
        o = _s([t for t in ts if t["day"] >= SPLIT]) or none
        if not a:
            lines.append(f"| {name} | 0 | | | | | | | no trades |")
            continue
        ok = i["pf"] > 1.1 and o["pf"] > 1.1 and i["n"] >= 30 and o["n"] >= 30
        weak = i["pf"] > 1 and o["pf"] > 1
        lines.append(f"| {name} | {a['n']} | {a['win']:.0%} | {a['r']:+.2f} | {a['avg']:+.3%} | {a['pf']:.2f} | "
                     f"{i['win']:.0%} / {i['pf']:.2f} | {o['win']:.0%} / {o['pf']:.2f} | "
                     f"{'KEEP' if ok else 'weak' if weak else 'drop'} |")
    return "\n".join(lines)


def load(folder=None):
    if folder:
        return {s: json.load(open(os.path.join(folder, f"m5_{s}.json"))) for s in SYMBOLS
                if os.path.exists(os.path.join(folder, f"m5_{s}.json"))}
    from .broker import Broker
    b = Broker()
    return {s: b.bars([s], "5Min", "2024-01-01", feed="sip", adjustment="all").get(s, []) for s in SYMBOLS}


if __name__ == "__main__":
    print(table(evaluate(load(sys.argv[1] if len(sys.argv) > 1 else None))))
