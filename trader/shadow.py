"""Replay the day's shadow trades: signals that got no slot (trader/run.py
writes them to trader/journal/shadow.csv). Each one is played out on the
day's 1-minute bars with its strategy's own stop, half-off, trail and 15:58
exit (strategies.simulate). The risk review then counts them with the live
trades, so every strategy reaches its 40-trade sample sooner.

    python -m trader.shadow [YYYY-MM-DD]
"""
import csv
import os
import sys
from datetime import date, datetime

from . import run, strategies
from .broker import Broker
from .config import Config

ET = run.ET


def load(cfg):
    path = run.shadow_path(cfg)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def _f(x):
    return float(x) if x not in ("", None) else None


def replay(broker, cfg, day):
    rows = load(cfg)
    todo = [r for r in rows if r["time"][:10] == day.isoformat() and not r.get("exit_time")]
    if not todo:
        return 0
    close_ = datetime(day.year, day.month, day.day, 16, 0, tzinfo=ET)
    open_ = close_.replace(hour=9, minute=30)
    ctx = run.day_data(broker, cfg, close_)
    syms = sorted({r["symbol"] for r in todo} | {"SPY"})
    bars = broker.bars(syms, "1Min", open_.isoformat(), end=close_.isoformat(), feed=cfg.data_feed)
    bars = {s: [b for b in bs if strategies.bar_time(b) < close_] for s, bs in bars.items()}
    spy = bars.get("SPY", [])
    for r in todo:
        t = {"time": r["time"], "qty": float(r["qty"] or 0), "entry": float(r["entry"]), "stop": float(r["stop"]),
             "target": _f(r["target"]), "half_at": _f(r["half_at"]), "trail": r["trail"] or None,
             "dir": int(r["dir"] or 1)}
        if not t["qty"]:
            continue
        res = strategies.simulate(t, bars.get(r["symbol"], []), spy if t["trail"] in ("band", "vwap_grid") else None,
                                  run.prior_close(ctx, "SPY"), ctx["sigma"])
        if res:
            r.update(res)
    with open(run.shadow_path(cfg), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=run.SHADOW_FIELDS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in run.SHADOW_FIELDS} for r in rows)
    return len(todo)


def results(cfg):
    """Replayed shadow trades as closed_trades-like dicts."""
    out = []
    for r in load(cfg):
        if not r.get("exit_time"):
            continue
        qty, entry, stop = float(r["qty"]), float(r["entry"]), float(r["stop"])
        out.append({"day": r["time"][:10], "symbol": r["symbol"], "qty": qty, "entry": entry, "stop": stop,
                    "pnl": float(r["pnl"]), "risk": qty * (entry - stop), "r": float(r["r"]), "how": r["how"],
                    "risk_taken": False, "group": r["strategy"], "shadow": True})
    return out


if __name__ == "__main__":
    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(ET).date()
    print(f"replayed {replay(Broker(), Config(), d)} shadow trades for {d}")
