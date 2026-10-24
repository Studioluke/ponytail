"""Paper swing tracker for multi-day trades, separate from the intraday bot.

Reads trader/journal/swing/plan.csv (one row per idea: entry zone, stop,
target, active window) and replays it on Alpaca daily bars against a
simulated account. It never places orders, so it cannot collide with the
day trader's positions or the risk manager's $300 limits.

    python -m trader.swing        # writes trader/journal/swing/report.md

Fill rules, all conservative:
    entry   first day the bar trades into the zone; at the open if the open
            is inside the zone (or below it but above the stop), else at
            entry_high
    stop    low <= stop exits at the stop (or the open if it gapped below)
    target  high >= target exits at the target; a day that hits both counts
            as the stop
    time    still open on exit_by exits at that day's close
Size: risk RISK of the starting cash per trade, capped by free cash.
"""
import csv
import sys
from datetime import date

PLAN = "trader/journal/swing/plan.csv"
REPORT = "trader/journal/swing/report.md"
START_CASH = 1000.0
RISK = 0.02


def load_plan(path=PLAN):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("entry_low", "entry_high", "stop", "target"):
            r[k] = float(r[k])
    return rows


def simulate(plan, bars, cash=START_CASH, risk=RISK):
    """Replay the plan day by day. bars: {symbol: [{'t','o','h','l','c'}, ...]}."""
    days = sorted({b["t"][:10] for bs in bars.values() for b in bs})
    by_day = {s: {b["t"][:10]: b for b in bs} for s, bs in bars.items()}
    open_pos, trades, done = {}, [], set()
    for d in days:
        for p in plan:
            s = p["symbol"]
            b = by_day.get(s, {}).get(d)
            if b is None or s in done or d < p["active_from"] or d > p["exit_by"]:
                continue
            if s not in open_pos:
                if b["l"] > p["entry_high"]:
                    continue
                o = b["o"]
                if p["entry_low"] <= o <= p["entry_high"] or p["stop"] < o < p["entry_low"]:
                    px = o
                elif o > p["entry_high"]:
                    px = p["entry_high"]
                else:
                    continue  # gapped through the stop: skip the day
                qty = min(risk * START_CASH / (px - p["stop"]), cash / px)
                if qty * px < 1:
                    continue
                cash -= qty * px
                open_pos[s] = {"qty": qty, "entry": px, "date": d}
            pos = open_pos[s]
            exit_px = why = None
            if b["l"] <= p["stop"]:
                exit_px, why = min(b["o"], p["stop"]), "stop"
            elif b["h"] >= p["target"]:
                exit_px, why = max(b["o"], p["target"]), "target"
            elif d == p["exit_by"]:
                exit_px, why = b["c"], "time"
            if exit_px is not None:
                cash += pos["qty"] * exit_px
                trades.append({"symbol": s, "in": pos["date"], "entry": pos["entry"], "out": d, "exit": exit_px,
                               "qty": pos["qty"], "pnl": pos["qty"] * (exit_px - pos["entry"]), "why": why})
                del open_pos[s]
                done.add(s)
    last = {s: bs[-1]["c"] for s, bs in bars.items() if bs}
    marks = {s: {**p, "last": last.get(s, p["entry"]),
                 "pnl": p["qty"] * (last.get(s, p["entry"]) - p["entry"])} for s, p in open_pos.items()}
    equity = cash + sum(m["qty"] * m["last"] for m in marks.values())
    return {"cash": cash, "equity": equity, "trades": trades, "open": marks}


def report(plan, res, today):
    lines = [f"# Paper swing tracker ({today})", "",
             f"Simulated ${START_CASH:,.0f} account, {RISK:.0%} risk per trade, no real or Alpaca orders.", "",
             f"**Equity ${res['equity']:,.2f}** ({res['equity'] / START_CASH - 1:+.1%}), cash ${res['cash']:,.2f}", "",
             "## Open", "| Symbol | In | Entry | Last | Qty | P&L |", "|---|---|---|---|---|---|"]
    lines += [f"| {s} | {m['date']} | {m['entry']:.2f} | {m['last']:.2f} | {m['qty']:.3f} | {m['pnl']:+.2f} |"
              for s, m in res["open"].items()] or ["| none | | | | | |"]
    lines += ["", "## Closed", "| Symbol | In | Entry | Out | Exit | Why | P&L |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {t['symbol']} | {t['in']} | {t['entry']:.2f} | {t['out']} | {t['exit']:.2f} | {t['why']} | {t['pnl']:+.2f} |"
              for t in res["trades"]] or ["| none | | | | | | |"]
    lines += ["", "## Plan", "| Symbol | Window | Entry zone | Stop | Target | Note |", "|---|---|---|---|---|---|"]
    lines += [f"| {p['symbol']} | {p['active_from']} to {p['exit_by']} | {p['entry_low']:g}-{p['entry_high']:g} | "
              f"{p['stop']:g} | {p['target']:g} | {p['note']} |" for p in plan]
    return "\n".join(lines) + "\n"


def main(argv):
    from .broker import Broker
    plan = load_plan()
    start = min(p["active_from"] for p in plan)
    today = date.today().isoformat()
    bars = Broker().bars([p["symbol"] for p in plan], "1Day", start) if today >= start else {}
    res = simulate(plan, bars)
    text = report(plan, res, today)
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
