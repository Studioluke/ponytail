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

from . import risk_manager, strategy
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


def _fills(broker, sym, since):
    flat = []
    for o in broker.closed_orders(since):
        flat.append(o)
        flat.extend(o.get("legs") or [])
    return [o for o in flat if o["symbol"] == sym and o.get("filled_at") and float(o["filled_qty"] or 0)]


def reconcile(broker, cfg, book, now):
    """Book realized P&L for trades that are now flat, and say why they closed."""
    held = {p["symbol"] for p in broker.positions()}
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0).isoformat()
    for sym, t in list(book.open.items()):
        if sym in held:
            continue
        fills = _fills(broker, sym, open_)
        if not any(o["side"] == "sell" for o in fills):
            continue  # buy never filled or sell still pending
        pnl = sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) * (1 if o["side"] == "sell" else -1)
                  for o in fills)
        sells = [o for o in fills if o["side"] == "sell"]
        exit_px = sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) for o in sells) / \
            sum(float(o["filled_qty"]) for o in sells)
        reason = t.get("exit_reason") or ("stop" if any(o["id"] == t.get("stop_order_id") for o in sells) else "other")
        book.record(pnl)
        del book.open[sym]
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": f"exit_{reason}", "qty": t["qty"],
                      "price": f"{exit_px:.2f}", "stop": t["stop"], "target": t["target"], "pnl": f"{pnl:.2f}",
                      "note": f"entry {t['entry']:.2f}, R = {(exit_px - t['entry']) / (t['entry'] - t['stop']):+.2f}"})
        log(f"{sym} closed ({reason}) at {exit_px:.2f}, P&L ${pnl:.2f}; day ${book.day_pnl:.2f}, week ${book.week_pnl:.2f}")


def manage(broker, cfg, book):
    """Take profit at the target. The resting stop order handles the downside."""
    for sym, t in book.open.items():
        if t.get("exit_reason"):
            continue
        px = broker.latest_price(sym, cfg.data_feed)
        if px >= t["target"]:
            if t.get("stop_order_id"):
                try:
                    broker.cancel(t["stop_order_id"])
                except RuntimeError:
                    pass
            broker.close_position(sym)
            t["exit_reason"] = "target"
            log(f"{sym} hit target {t['target']} (last {px:.2f}), closing")


def gap_ok(broker, cfg, sym, bars, now):
    """Vault rule: skip a symbol whose open gapped more than max_gap from the prior close."""
    if not bars:
        return True, ""
    start = (now - timedelta(days=7)).date().isoformat()
    daily = broker.bars([sym], "1Day", start, end=now.date().isoformat(), feed=cfg.data_feed).get(sym, [])
    prior = [b for b in daily if b["t"][:10] < now.date().isoformat()]
    if not prior:
        return True, ""
    gap = bars[0]["o"] / prior[-1]["c"] - 1
    return abs(gap) <= cfg.max_gap, f"gap {gap:+.2%} vs prior close {prior[-1]['c']}"


def step(broker, cfg, book, now):
    t = now.time()
    killed = risk_manager.kill_reason(cfg)
    if killed:
        if f"kill:{book.day}" not in book.seen_orders:
            book.seen_orders.append(f"kill:{book.day}")
            journal(cfg, {"time": now.isoformat(), "event": "kill", "note": killed})
        if broker.positions() or broker.open_orders():
            log(f"kill switch on ({killed}), flattening")
            for tr in book.open.values():
                tr.setdefault("exit_reason", "kill")
            broker.flatten()
        reconcile(broker, cfg, book, now)
        return
    if t >= cfg.flatten_at:
        if broker.positions() or broker.open_orders():
            log("flattening for the close")
            for sym, tr in book.open.items():
                tr.setdefault("exit_reason", "eod")
            broker.flatten()
        return
    reconcile(broker, cfg, book, now)
    manage(broker, cfg, book)
    risk_manager.protect(broker, cfg, book, journal, log, now)
    reason = book.halted(cfg)
    if reason:
        if f"halt:{book.day}" not in book.seen_orders:
            book.seen_orders.append(f"halt:{book.day}")
            journal(cfg, {"time": now.isoformat(), "event": "halted", "note": reason})
        log(f"halted: {reason}")
        return
    if t < cfg.session_start or t > cfg.last_entry:
        return
    # Only the configured capital is ours to use, whatever the account holds.
    positions = broker.positions()
    account = broker.account()
    used = sum(abs(float(p["cost_basis"])) for p in positions)
    cash = min(float(account["cash"]), cfg.capital - used)
    bars = todays_bars(broker, cfg, now)
    research = risk_manager.research_verdicts(cfg, book.day)
    for sym in cfg.symbols:
        if sym in book.traded_today:
            continue
        sig = strategy.check(sym, bars.get(sym, []), cfg.opening_range_minutes, cfg.reward_risk)
        if not sig:
            continue
        book.traded_today.append(sym)
        ok, gap_note = gap_ok(broker, cfg, sym, bars.get(sym, []), now)
        if not ok:
            journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "skip", "price": f"{sig.entry:.2f}",
                          "note": f"{sig.reason}; skipped, {gap_note} exceeds {cfg.max_gap:.2%}"})
            log(f"{sym} signal skipped: {gap_note}")
            continue
        qty = size(cfg.capital, cfg.risk_per_trade, sig.entry, sig.stop, cash, cfg.fractional)
        if not qty:
            journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "skip", "price": f"{sig.entry:.2f}",
                          "note": f"{sig.reason}; skipped, size rounds to 0"})
            log(f"{sym} signal skipped, size rounds to 0 ({sig.reason})")
            continue
        last_bar = datetime.fromisoformat(bars[sym][-1]["t"].replace("Z", "+00:00"))
        decision = risk_manager.check_entry(cfg, book, sig, qty, now, account, positions, last_bar,
                                            broker.latest_price(sym, cfg.data_feed), research)
        if not decision.ok:
            journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "risk_block", "qty": qty,
                          "price": f"{sig.entry:.2f}", "stop": sig.stop, "target": sig.target,
                          "note": f"{sig.reason}; vetoed: {decision}"})
            log(f"{sym} signal vetoed by risk manager: {decision}")
            continue
        order = broker.buy_market(sym, qty, f"orb-{book.day}-{sym}")
        fill = None
        for _ in range(20):
            o = broker.order(order["id"])
            if o["status"] == "filled":
                fill = float(o["filled_avg_price"])
                break
            _time.sleep(1)
        entry = fill or sig.entry
        try:
            stop_id = broker.sell_stop(sym, qty, sig.stop)["id"]
        except RuntimeError as e:
            stop_id = None  # protect() below retries once, then closes the position
            log(f"{sym} stop order failed: {e}")
        book.open[sym] = {"qty": qty, "entry": entry, "stop": sig.stop, "target": sig.target,
                          "stop_order_id": stop_id}
        positions.append({"symbol": sym, "cost_basis": qty * entry})
        cash -= qty * entry
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "buy", "qty": qty,
                      "price": f"{entry:.2f}", "stop": sig.stop, "target": sig.target,
                      "note": f"{sig.reason}; {gap_note}; risk ${qty * (entry - sig.stop):.2f}"})
        log(f"BUY {qty} {sym} @ {entry:.2f} stop {sig.stop} target {sig.target}: {sig.reason}")
        if not stop_id:
            risk_manager.protect(broker, cfg, book, journal, log, now)


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
