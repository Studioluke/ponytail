"""Swing screener: which liquid US stocks and ETFs suit the playbook's swing setups, and which fire now.

    python -m trader.screener              # writes trader/journal/swing/screener.md
    python -m trader.screener --plan       # also adds firing setups to the swing plan

For each symbol in UNIVERSE (plus today's most-active names that pass the
liquidity filter) it pulls daily bars since 2016 and scores:

    history   how the two core setups (STRETCH and RSI2+IBS, trader/patterns.py)
              did on that symbol: trades, win rate, profit factor
    today     whether a setup fires on the latest close, or how far price is
              from the STRETCH trigger
    fit       price over $10, 20-day dollar volume over $100M, above the 200-day
              average, daily ATR 1.5-6% of price (enough movement, not a lottery ticket)

Ranking is by history first: a symbol where the setups never worked is not
a swing candidate however good today's chart looks. Read-only; places no orders.
"""
import csv
import sys
from datetime import date, timedelta

from . import patterns as P

OUT = "trader/journal/swing/screener.md"

UNIVERSE = (
    "SPY,QQQ,IWM,DIA,XLK,XLF,XLE,XLV,XLI,XLY,XLP,XLU,XLB,XLC,SMH,XBI,KRE,GLD,"
    "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,AVGO,AMD,NFLX,COST,ORCL,CRM,ADBE,INTC,QCOM,MU,TXN,AMAT,LRCX,"
    "PANW,CRWD,FTNT,ZS,NET,OKTA,NOW,SNOW,PLTR,SHOP,UBER,ABNB,PYPL,SQ,COIN,"
    "JPM,BAC,GS,MS,WFC,C,V,MA,AXP,BRK.B,UNH,LLY,JNJ,ABBV,MRK,PFE,TMO,ISRG,"
    "HD,LOW,WMT,TGT,MCD,SBUX,NKE,KO,PEP,PG,DIS,CMCSA,T,VZ,"
    "XOM,CVX,COP,CAT,DE,GE,BA,LMT,RTX,HON,UPS").split(",")

STRETCH = "STRETCH: close < 10d avg - 2 ATR, IBS<0.25, above 200d, exit >5d avg"
RSI_IBS = "RSI2<5 + IBS<0.2 above 200d, exit > prior high"
LEVERED = ("SOXL", "SOXS", "TQQQ", "SQQQ", "TSLL", "TSLG", "NVD", "MSTZ", "SPDN", "QID", "RWM", "SNXX", "AIOK")


def history(bars):
    out = {}
    for name in (STRETCH, RSI_IBS):
        entry, exit_fn, hold, stop = P.RULES[name]
        out[name] = P.stats(P.run_rule(bars, entry, exit_fn, hold, stop))
    return out


def today(bars):
    x, i = P.Ctx(bars), len(bars) - 1
    b = bars[i]
    trigger = x.sma10[i] - 2.0 * x.atr[i]
    fires = [n for n in (STRETCH, RSI_IBS) if P.RULES[n][0](x, i)]
    return {"close": b["c"], "date": b["t"][:10], "uptrend": x.uptrend(i), "rsi2": x.rsi2[i],
            "ibs": P.ibs(b), "atr_pct": x.atr[i] / b["c"], "trigger": trigger,
            "to_trigger": b["c"] / trigger - 1, "fires": fires,
            "dollar_vol": sum(z["c"] * z["v"] for z in bars[-20:]) / 20}


def score(h):
    s, r = h[STRETCH], h[RSI_IBS]
    n = s.get("n", 0) + r.get("n", 0)
    if n < 8:
        return 0.0
    wins = s.get("n", 0) * s.get("win", 0) + r.get("n", 0) * r.get("win", 0)
    pf = min((s.get("pf", 0) * s.get("n", 0) + r.get("pf", 0) * r.get("n", 0)) / n, 5)
    return round(wins / n * 50 + pf * 10, 1)


def plan_rows(rows, existing):
    """Swing-plan rows (trader/swing.py format) for setups firing on the latest close.

    Entry zone: within 1% under to 0.5% over the signal close (swing.py fills from the
    next day). Stop 2.5 ATR under the close, the stop the backtest kept profitable;
    target the 10-day average, where the setup's "close above the 5-day average" exit
    usually lands; out after two weeks at most."""
    busy = {(p["symbol"]) for p in existing}
    out = []
    for r in rows:
        t = r["t"]
        if not (t["fires"] and r["fit"]) or r["sym"] in busy:
            continue
        x = P.Ctx(r["bars"])
        i = len(r["bars"]) - 1
        start = date.fromisoformat(t["date"]) + timedelta(days=1)
        out.append({"symbol": r["sym"], "active_from": start.isoformat(),
                    "exit_by": (start + timedelta(days=14)).isoformat(),
                    "entry_low": round(t["close"] * 0.99, 2), "entry_high": round(t["close"] * 1.005, 2),
                    "stop": round(t["close"] - 2.5 * x.atr[i], 2), "target": round(x.sma10[i], 2),
                    "note": f"Auto: {t['fires'][0].split(':')[0].split(' above')[0]} setup (playbook), score {r['score']}"})
    return out


def add_to_plan(new, path="trader/journal/swing/plan.csv"):
    fields = ["symbol", "active_from", "exit_by", "entry_low", "entry_high", "stop", "target", "note"]
    with open(path, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=fields).writerows(new)


def most_actives(broker, top=50):
    from .config import DATA_URL
    try:
        d = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/most-actives", params={"by": "trades", "top": top})
        return [x["symbol"] for x in d.get("most_actives", []) if x["symbol"] not in LEVERED]
    except RuntimeError:
        return []


def screen(bars_by_symbol):
    rows = []
    for sym, bars in bars_by_symbol.items():
        if len(bars) < 260:
            continue
        t = today(bars)
        fit = t["close"] > 10 and t["dollar_vol"] > 1e8 and 0.015 <= t["atr_pct"] <= 0.06
        rows.append({"sym": sym, "h": history(bars), "t": t, "fit": fit, "bars": bars})
    for r in rows:
        r["score"] = score(r["h"]) if r["fit"] else 0.0
    return sorted(rows, key=lambda r: (-r["score"], r["sym"]))


def report(rows, top=25):
    asof = max(r["t"]["date"] for r in rows)
    firing = [r for r in rows if r["t"]["fires"] and r["fit"]]
    near = sorted([r for r in rows if r["fit"] and r["t"]["uptrend"] and not r["t"]["fires"]
                   and 0 < r["t"]["to_trigger"] < 0.03], key=lambda r: r["t"]["to_trigger"])
    out = [f"# Swing screener, close of {asof}", "",
           "Setups from trader/patterns.py, scored on each symbol's own history since 2016. "
           "Simulated/paper only; not advice.", "",
           "## Firing on the latest close", ""]
    if firing:
        out += ["| Symbol | Setup | Close | RSI2 | IBS | Score |", "|---|---|---|---|---|---|"]
        for r in firing:
            t = r["t"]
            out.append(f"| {r['sym']} | {'; '.join(n.split(':')[0].split(' above')[0] for n in t['fires'])} | "
                       f"{t['close']:.2f} | {t['rsi2']:.0f} | {t['ibs']:.2f} | {r['score']} |")
    else:
        out.append("None. The setups buy sharp dips in uptrends, so quiet or rising days fire nothing.")
    out += ["", "## Within 3% of the STRETCH trigger (watch list)", ""]
    if near:
        out += ["| Symbol | Close | Trigger (10d avg - 2 ATR) | Distance | Score |", "|---|---|---|---|---|"]
        for r in near[:15]:
            t = r["t"]
            out.append(f"| {r['sym']} | {t['close']:.2f} | {t['trigger']:.2f} | {t['to_trigger']:.1%} | {r['score']} |")
    else:
        out.append("None.")
    out += ["", f"## Best swing candidates by history (top {top})", "",
            "| Rank | Symbol | Score | STRETCH trades / win / PF | RSI2+IBS trades / win / PF | ATR % | Above 200d |",
            "|---|---|---|---|---|---|---|"]
    for k, r in enumerate([r for r in rows if r["fit"]][:top], 1):
        s, q, t = r["h"][STRETCH], r["h"][RSI_IBS], r["t"]
        fmt = lambda m: f"{m.get('n', 0)} / {m.get('win', 0):.0%} / {m.get('pf', 0):.2f}" if m.get("n") else "0"
        out.append(f"| {k} | {r['sym']} | {r['score']} | {fmt(s)} | {fmt(q)} | {t['atr_pct']:.1%} | "
                   f"{'yes' if t['uptrend'] else 'no'} |")
    out += ["", "Score = 50 x win rate + 10 x profit factor (capped at 5), pooled over both setups; "
            "0 when the symbol fails the price, liquidity or volatility filter. "
            "The universe is today's large caps, so history flatters it (survivorship)."]
    return "\n".join(out) + "\n"


def main(argv):
    from .broker import Broker
    b = Broker()
    syms = list(dict.fromkeys(list(UNIVERSE) + most_actives(b)))
    bars = {}
    for k in range(0, len(syms), 40):
        bars.update(b.bars(syms[k:k + 40], "1Day", "2016-01-01", feed="sip", adjustment="all"))
    rows = screen(bars)
    text = report(rows)
    with open(OUT, "w") as f:
        f.write(text)
    print(text)
    if "--plan" in argv:
        from .swing import load_plan
        new = plan_rows(rows, load_plan())
        add_to_plan(new)
        print(f"added {len(new)} setups to the swing plan: {', '.join(n['symbol'] for n in new) or 'none'}")


if __name__ == "__main__":
    main(sys.argv[1:])
