"""Paper-trading loop.

    python -m trader.run check   # verify keys, account, clock, data
    python -m trader.run once    # one decision pass, then exit
    python -m trader.run loop    # run until the close, polling each minute
"""
import csv
import os
import sys
import time as _time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import strategy
from .broker import Broker
from .config import Config
from .risk import Book, size

ET = ZoneInfo("America/New_York")


def log(msg):
    print(f"{datetime.now(ET):%Y-%m-%d %H:%M:%S} ET  {msg}", flush=True)


def journal(cfg, row):
    new = not os.path.exists(cfg.journal_path)
    os.makedirs(os.path.dirname(cfg.journal_path) or ".", exist_ok=True)
    with open(cfg.journal_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "symbol", "event", "qty", "price", "stop", "target", "pnl", "note"])
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in w.fieldnames})


def check(broker, cfg):
    a = broker.account()
    c = broker.clock()
    log(f"account {a['status']}  equity ${float(a['equity']):,.2f}  cash ${float(a['cash']):,.2f}  "
        f"sizing against ${cfg.capital:,.2f}")
    log(f"market {'OPEN' if c['is_open'] else 'closed'}; next open {c['next_open']}")
    start = (datetime.now(ET) - timedelta(days=7)).date().isoformat()
    bars = broker.bars(list(cfg.symbols), "1Day", start, feed=cfg.data_feed)
    for s in cfg.symbols:
        b = (bars.get(s) or [None])[-1]
        log(f"{s} last daily close {b['c'] if b else 'n/a'} ({b['t'][:10] if b else ''})")


def todays_bars(broker, cfg, now):
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    bars = broker.bars(list(cfg.symbols), "1Min", open_.isoformat(), feed=cfg.data_feed)
    # Drop the bar still forming.
    cutoff = now.replace(second=0, microsecond=0)
    return {s: [b for b in bs if datetime.fromisoformat(b["t"].replace("Z", "+00:00")) < cutoff]
            for s, bs in bars.items()}


def reconcile(broker, cfg, book, now):
    """Book realized P&L for symbols we traded today that are now flat."""
    held = {p["symbol"] for p in broker.positions()}
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    orders = broker.closed_orders(open_.isoformat())
    flat = []
    for o in orders:
        flat.append(o)
        flat.extend(o.get("legs") or [])
    for sym in book.traded_today:
        if sym in held or f"{book.day}:{sym}" in book.seen_orders:
            continue
        fills = [o for o in flat if o["symbol"] == sym and o.get("filled_at")]
        if not fills:
            continue
        pnl = sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) * (1 if o["side"] == "sell" else -1)
                  for o in fills)
        book.record(pnl)
        book.seen_orders.append(f"{book.day}:{sym}")
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "closed", "pnl": f"{pnl:.2f}"})
        log(f"{sym} closed, P&L ${pnl:.2f}; day ${book.day_pnl:.2f}, week ${book.week_pnl:.2f}")


def step(broker, cfg, book, now):
    t = now.time()
    if t >= cfg.flatten_at:
        if broker.positions() or broker.open_orders():
            log("flattening for the close")
            broker.flatten()
        return
    reconcile(broker, cfg, book, now)
    reason = book.halted(cfg)
    if reason:
        log(f"halted: {reason}")
        return
    if t < cfg.session_start or t > cfg.last_entry:
        return
    cash = float(broker.account()["cash"])
    bars = todays_bars(broker, cfg, now)
    for sym in cfg.symbols:
        if sym in book.traded_today:
            continue
        sig = strategy.check(sym, bars.get(sym, []), cfg.opening_range_minutes, cfg.reward_risk)
        if not sig:
            continue
        qty = size(cfg.capital, cfg.risk_per_trade, sig.entry, sig.stop, cash)
        if qty < 1:
            log(f"{sym} signal skipped, size rounds to 0 shares ({sig.reason})")
            book.traded_today.append(sym)
            continue
        broker.bracket_buy(sym, qty, sig.stop, sig.target, f"orb-{book.day}-{sym}")
        book.traded_today.append(sym)
        cash -= qty * sig.entry
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "buy", "qty": qty,
                      "price": f"{sig.entry:.2f}", "stop": sig.stop, "target": sig.target, "note": sig.reason})
        log(f"BUY {qty} {sym} ~{sig.entry:.2f} stop {sig.stop} target {sig.target}: {sig.reason}")


def run(mode):
    cfg = Config()
    broker = Broker()
    if mode == "check":
        return check(broker, cfg)
    book = Book.load(cfg.state_path)
    while True:
        now = datetime.now(ET)
        iso = now.isocalendar()
        book.roll(now.date().isoformat(), f"{iso.year}-W{iso.week:02d}")
        if broker.clock()["is_open"]:
            step(broker, cfg, book, now)
        elif mode == "loop":
            log("market closed")
        book.save(cfg.state_path)
        if mode == "once" or now.time() >= cfg.flatten_at:
            if mode == "loop" and now.time() >= cfg.flatten_at:
                _time.sleep(5)  # let the flatten orders fill
                reconcile(broker, cfg, book, now)
                book.save(cfg.state_path)
                log(f"done for the day: P&L ${book.day_pnl:.2f}, week ${book.week_pnl:.2f}")
            return
        if mode == "loop" and not broker.clock()["is_open"]:
            return
        _time.sleep(60 - datetime.now().second + 2)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "check")
