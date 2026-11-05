"""Paper-trading loop.

    python -m trader.run check   # verify keys, account, clock, data
    python -m trader.run once    # one decision pass, then exit
    python -m trader.run loop    # run until the close, polling each minute
"""
import csv
import math
import os
import sys
import time as _time
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import requests

from . import risk_manager, strategies, strategy
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


def todays_bars(broker, cfg, now, symbols=None):
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    bars = broker.bars(sorted(symbols or cfg.symbols), "1Min", open_.isoformat(), feed=cfg.data_feed)
    # Drop the bar still forming.
    cutoff = now.replace(second=0, microsecond=0)
    return {s: [b for b in bs if datetime.fromisoformat(b["t"].replace("Z", "+00:00")) < cutoff]
            for s, bs in bars.items()}


def _fills(broker, sym, since, after=None):
    flat = []
    for o in broker.closed_orders(since):
        flat.append(o)
        flat.extend(o.get("legs") or [])
    out = [o for o in flat if o["symbol"] == sym and o.get("filled_at") and float(o["filled_qty"] or 0)]
    if after:
        # Several strategies can trade the same symbol in a day (SPY): count
        # only the fills of this trade.
        cut = datetime.fromisoformat(after)
        out = [o for o in out if datetime.fromisoformat(o["filled_at"].replace("Z", "+00:00")) >= cut]
    return out


def reconcile(broker, cfg, book, now):
    """Book realized P&L for trades that are now flat, and say why they closed."""
    held = {p["symbol"] for p in broker.positions()}
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0).isoformat()
    for sym, t in list(book.open.items()):
        if sym in held:
            continue
        fills = _fills(broker, sym, open_, t.get("opened_at"))
        if not any(o["side"] == "sell" for o in fills):
            continue  # buy never filled or sell still pending
        pnl = sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) * (1 if o["side"] == "sell" else -1)
                  for o in fills)
        sells = [o for o in fills if o["side"] == "sell"]
        exit_px = sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) for o in sells) / \
            sum(float(o["filled_qty"]) for o in sells)
        reason = t.get("exit_reason") or ("stop" if any(o["id"] == t.get("stop_order_id") for o in sells) else "other")
        stop0 = t.get("stop0", t["stop"])
        book.record(pnl, t.get("strategy"))
        del book.open[sym]
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": f"exit_{reason}", "qty": t.get("qty0", t["qty"]),
                      "price": f"{exit_px:.2f}", "stop": stop0, "target": t.get("target") or "", "pnl": f"{pnl:.2f}",
                      "note": f"{'[' + t['strategy'] + '] ' if t.get('strategy') else ''}entry {t['entry']:.2f}, "
                              f"R = {(exit_px - t['entry']) / (t['entry'] - stop0):+.2f}"})
        log(f"{sym} closed ({reason}) at {exit_px:.2f}, P&L ${pnl:.2f}; day ${book.day_pnl:.2f}, week ${book.week_pnl:.2f}")


def _clear_stop(broker, t):
    """Cancel the resting stop and wait for it to clear: selling while it still
    holds the shares fails with 403 (10-27, SOFI)."""
    if not t.get("stop_order_id"):
        return
    try:
        broker.cancel(t["stop_order_id"])
    except RuntimeError:
        pass
    for _ in range(10):
        if broker.order(t["stop_order_id"])["status"] in ("canceled", "filled", "expired", "rejected"):
            break
        _time.sleep(1)


def manage(broker, cfg, book, now=None, bars=None, spy=None, grid=False):
    """Targets, the control strategy's half-off at 2R, and the trailing exits
    (strategies.exit_action). The resting stop order handles the downside."""
    bars = bars or {}
    for sym, t in book.open.items():
        if t.get("exit_reason"):
            continue
        px = broker.latest_price(sym, cfg.data_feed)
        sb = bars.get(sym) or []
        act = strategies.exit_action(t, px, sb[-1]["c"] if sb else None, strategy.vwap(sb) if sb else None,
                                     spy, grid)
        if not act:
            continue
        _clear_stop(broker, t)
        if act[0] == "half":
            half = math.floor(t["qty"] / 2 * 1000) / 1000
            try:
                broker.sell_market(sym, half)
            except RuntimeError as e:
                log(f"{sym} half sell failed, retrying next pass: {e}")
                t["stop_order_id"] = None  # protect() re-places the stop
                continue
            t.setdefault("qty0", t["qty"])
            t["qty"] = round(t["qty"] - half, 3)
            t["half_done"] = True
            t["stop"] = max(t["stop"], round(t["entry"], 2))  # rest rides at breakeven or better
            try:
                t["stop_order_id"] = broker.sell_stop(sym, t["qty"], t["stop"])["id"]
            except RuntimeError as e:
                t["stop_order_id"] = None
                log(f"{sym} stop re-place after half failed: {e}")
            journal(cfg, {"time": (now or datetime.now(ET)).isoformat(), "symbol": sym, "event": "partial",
                          "qty": half, "price": f"{px:.2f}", "stop": t["stop"],
                          "note": f"[{t.get('strategy')}] sold half at 2R ({t['half_at']}); rest trails VWAP"})
            log(f"{sym} sold half ({half}) at {px:.2f}; stop to {t['stop']}")
            continue
        try:
            broker.close_position(sym)
        except RuntimeError as e:
            log(f"{sym} {act[1]} close failed, retrying next pass: {e}")
            continue
        t["exit_reason"] = act[1]
        if act[1] == "target":
            log(f"{sym} hit target {t['target']} (last {px:.2f}), closing")
        else:
            log(f"{sym} {act[1]} exit at {px:.2f}, closing")


# Per-day data the strategies share: prior daily bars (ATR, prior close) and
# the SPY noise-area sigma. Fetched once a day per process.
_DAY = {}


def day_data(broker, cfg, now):
    day = now.date().isoformat()
    if _DAY.get("day") == day:
        return _DAY
    syms = sorted(set(cfg.watchlist) | set(cfg.symbols) | {"SPY", "SH", "IWM"})
    start = (now - timedelta(days=45)).date().isoformat()
    daily = broker.bars(syms, "1Day", start, end=day, feed=cfg.data_feed)
    prior = {s: [b for b in bs if b["t"][:10] < day] for s, bs in daily.items()}
    dates = [b["t"][:10] for b in prior.get("SPY", [])][-strategies.NOISE_DAYS:]
    sigma = {}
    if dates:
        mins = broker.bars(["SPY"], "1Min",
                           datetime.fromisoformat(dates[0]).replace(hour=9, minute=30, tzinfo=ET).isoformat(),
                           end=now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
                           feed=cfg.data_feed).get("SPY", [])
        by_day = {}
        for b in mins:
            bt = strategies.bar_time(b)
            if time(9, 30) <= bt.time() < time(16, 0):
                by_day.setdefault(bt.date().isoformat(), []).append(b)
        sigma = strategies.noise_sigma([by_day[d] for d in dates if d in by_day])
    _DAY.clear()
    _DAY.update(day=day, prior=prior, dates=dates, sigma=sigma)
    return _DAY


def prior_close(ctx, sym):
    p = ctx["prior"].get(sym) or []
    return p[-1]["c"] if p else None


def gap_ok(broker, cfg, sym, bars, now, ctx=None):
    """Vault rule: skip a symbol whose open gapped more than max_gap from the prior close."""
    if not bars:
        return True, ""
    if ctx is not None:
        pc = prior_close(ctx, sym)
    else:
        start = (now - timedelta(days=7)).date().isoformat()
        daily = broker.bars([sym], "1Day", start, end=now.date().isoformat(), feed=cfg.data_feed).get(sym, [])
        prior = [b for b in daily if b["t"][:10] < now.date().isoformat()]
        pc = prior[-1]["c"] if prior else None
    if not pc:
        return True, ""
    gap = bars[0]["o"] / pc - 1
    return abs(gap) <= cfg.max_gap, f"gap {gap:+.2%} vs prior close {pc}"


def shadow_path(cfg):
    return os.path.join(os.path.dirname(cfg.journal_path) or ".", "shadow.csv")


SHADOW_FIELDS = ["time", "strategy", "symbol", "qty", "entry", "stop", "target", "half_at", "trail", "dir",
                 "why", "note", "exit_time", "exit_price", "how", "pnl", "r"]


def shadow(cfg, now, sig, qty, why, trail=None, d=1):
    """Log a signal that got no slot, so trader/shadow.py can replay it."""
    path = shadow_path(cfg)
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SHADOW_FIELDS)
        if new:
            w.writeheader()
        w.writerow({"time": now.isoformat(), "strategy": sig.strategy, "symbol": sig.symbol, "qty": qty,
                    "entry": f"{sig.entry:.4f}", "stop": sig.stop, "target": sig.target or "",
                    "half_at": sig.half_at or "", "trail": trail or "", "dir": d, "why": why, "note": sig.reason})
    log(f"{sig.symbol} [{sig.strategy}] shadow trade: {why}")


# Veto reasons that mean "no room", not "bad trade": those signals become
# shadow trades so the strategy's sample keeps growing.
CAPACITY = ("already holding", "positions open, max", "circuit breaker", "exposure over")


def feedcheck(broker, cfg, book, now):
    """Item 7 of the 11-04 research: log IEX vs SIP 9:30-9:35 and 9:30-9:45
    ranges once a day (SIP is free once it is 15 minutes old)."""
    if book.flags.get("feedcheck") or now.time() < time(9, 52):
        return
    book.flags["feedcheck"] = True
    syms = ["SPY", "QQQ"] + [c["symbol"] for c in (book.sip_watch or [])][:8]
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    end = (open_ + timedelta(minutes=14, seconds=59)).isoformat()
    try:
        feeds = {f: broker.bars(syms, "1Min", open_.isoformat(), end=end, feed=f) for f in ("iex", "sip")}
    except RuntimeError as e:
        log(f"feed check skipped: {str(e)[:120]}")
        return
    path = os.path.join(os.path.dirname(cfg.journal_path) or ".", "feedcheck.csv")
    new = not os.path.exists(path)
    cols = ["day", "symbol"] + [f"{f}_{k}" for f in ("iex", "sip") for k in ("5h", "5l", "15h", "15l", "5v")]
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        if new:
            w.writeheader()
        for s in syms:
            row = {"day": book.day, "symbol": s}
            for f, data in feeds.items():
                bs = data.get(s) or []
                if len(bs) < 5:
                    continue
                row.update({f"{f}_5h": max(b["h"] for b in bs[:5]), f"{f}_5l": min(b["l"] for b in bs[:5]),
                            f"{f}_15h": max(b["h"] for b in bs[:15]), f"{f}_15l": min(b["l"] for b in bs[:15]),
                            f"{f}_5v": sum(b["v"] for b in bs[:5])})
            w.writerow(row)
    log(f"feed check: IEX vs SIP logged for {', '.join(syms)}")


def sip_scan(broker, cfg, book, now, ctx):
    """At 9:35, rank the watchlist by 9:30-9:35 relative volume (strategies.stocks_in_play)."""
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    end = (open_ + timedelta(minutes=4, seconds=59)).isoformat()
    wl = list(cfg.watchlist)
    first = {s: bs[0] for s, bs in broker.bars(wl, "5Min", open_.isoformat(), end=end, feed=cfg.data_feed).items()
             if bs and strategies.bar_time(bs[0]).time() == time(9, 30)}
    if not first:
        return None  # bar not published yet; try next minute
    hist = ctx.get("sip_hist") or sip_history(broker, cfg, ctx)
    ranked = strategies.stocks_in_play(first, hist, ctx["prior"])
    journal(cfg, {"time": now.isoformat(), "event": "sip_scan",
                  "note": "[sip_orb] top RVOL: " + (", ".join(f"{c['symbol']} {c['rvol']}x {'green' if c['green'] else 'red'}"
                                                             for c in ranked) or "none")})
    log("stocks in play: " + (", ".join(f"{c['symbol']} {c['rvol']}x{'' if c['green'] else ' (red)'}"
                                         for c in ranked) or "none"))
    return ranked


def sip_history(broker, cfg, ctx):
    """9:30-9:35 volume for each of the last 14 sessions. Slow (14 requests),
    so step() fetches it between 9:30 and 9:35, before the scan needs it."""
    wl = list(cfg.watchlist)
    hist = {}
    for d in ctx["dates"]:
        o = datetime.fromisoformat(d).replace(hour=9, minute=30, tzinfo=ET)
        for s, bs in broker.bars(wl, "5Min", o.isoformat(), end=(o + timedelta(minutes=4, seconds=59)).isoformat(),
                                 feed=cfg.data_feed).items():
            if bs:
                hist.setdefault(s, []).append(bs[0]["v"])
    ctx["sip_hist"] = hist
    return hist


def step(broker, cfg, book, now):
    cfg = risk_manager.day_config(cfg, book.day)
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
    ctx = day_data(broker, cfg, now)
    if book.sip_watch is None and t < strategies.SIP_SCAN_AT and "sip_hist" not in ctx:
        try:
            sip_history(broker, cfg, ctx)
        except RuntimeError as e:
            log(f"stocks-in-play history fetch failed, retrying: {str(e)[:120]}")
    watch = [c["symbol"] for c in (book.sip_watch or [])] if t <= strategies.SIP_LAST_ENTRY else []
    need = set(book.open) | set(cfg.core_symbols) | {"SPY", "SH"} | set(watch)
    bars = todays_bars(broker, cfg, now, need)
    spy_bars = bars.get("SPY") or []
    spy_pc = prior_close(ctx, "SPY")
    bands = strategies.noise_bands(spy_bars, spy_pc, ctx["sigma"])
    spy = {"close": spy_bars[-1]["c"], "vwap": strategy.vwap(spy_bars),
           "upper": bands[0] if bands else None, "lower": bands[1] if bands else None} if spy_bars else None
    key = strategies.on_noise_grid(now)
    grid = key is not None and book.flags.get("grid") != key
    if grid:
        book.flags["grid"] = key
    manage(broker, cfg, book, now, bars, spy, grid)
    risk_manager.protect(broker, cfg, book, journal, log, now)
    feedcheck(broker, cfg, book, now)
    reason = book.money_halt(cfg)
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
    state = {"cash": min(float(account["cash"]), cfg.capital - used)}
    research = risk_manager.research_verdicts(cfg, book.day)
    fomc = risk_manager.fomc_day(cfg, book.day)
    approved = set(cfg.symbols) | set(cfg.watchlist) | {"SPY", "SH", "IWM"}

    def enter(sig, trail=None, d=1, cap_frac=1.0, research_view=None):
        name = sig.strategy
        risk_frac = strategies.RISK_FRAC[name] / (2 if fomc else 1)
        # Size as if the fill slips by max_slippage, so a fill a few cents
        # above the signal stays within the risk cap (10-27: SOFI, UPS).
        qty = size(cfg.capital, risk_frac, sig.entry * (1 + cfg.max_slippage), sig.stop,
                   min(max(state["cash"], 0), cfg.capital * cfg.max_position_frac * cap_frac), cfg.fractional)
        held_by = [s for s, tr in book.open.items() if tr.get("strategy") == name]
        if len(held_by) >= strategies.SLOTS[name]:
            full = size(cfg.capital, risk_frac, sig.entry, sig.stop, cfg.capital * cfg.max_position_frac * cap_frac,
                        cfg.fractional)
            return shadow(cfg, now, sig, full, f"{name} slots full ({', '.join(held_by)})", trail, d)
        if not qty:
            full = size(cfg.capital, risk_frac, sig.entry, sig.stop, cfg.capital * cfg.max_position_frac * cap_frac,
                        cfg.fractional)
            if full:
                return shadow(cfg, now, sig, full, "no cash left under the $300 cap", trail, d)
            journal(cfg, {"time": now.isoformat(), "symbol": sig.symbol, "event": "skip", "price": f"{sig.entry:.2f}",
                          "note": f"[{name}] {sig.reason}; skipped, size rounds to 0"})
            log(f"{sig.symbol} [{name}] signal skipped, size rounds to 0")
            return
        sb = bars.get(sig.symbol) or []
        last_bar = datetime.fromisoformat(sb[-1]["t"].replace("Z", "+00:00")) if sb else None
        decision = risk_manager.check_entry(cfg, book, sig, qty, now, account, positions, last_bar,
                                            broker.latest_price(sig.symbol, cfg.data_feed),
                                            research if research_view is None else research_view, fomc,
                                            strict=True, approved=approved)
        if not decision.ok:
            if all(any(c in r for c in CAPACITY) for r in decision.reasons):
                return shadow(cfg, now, sig, qty, str(decision), trail, d)
            journal(cfg, {"time": now.isoformat(), "symbol": sig.symbol, "event": "risk_block", "qty": qty,
                          "price": f"{sig.entry:.2f}", "stop": sig.stop, "target": sig.target or "",
                          "note": f"[{name}] {sig.reason}; vetoed: {decision}"})
            log(f"{sig.symbol} [{name}] signal vetoed by risk manager: {decision}")
            return
        opened_at = now.astimezone(ET).replace(microsecond=0).isoformat()
        order = broker.buy_market(sig.symbol, qty, f"{name}-{book.day}-{sig.symbol}-{now:%H%M}")
        fill = None
        for _ in range(20):
            o = broker.order(order["id"])
            if o["status"] == "filled":
                fill = float(o["filled_avg_price"])
                break
            _time.sleep(1)
        entry = fill or sig.entry
        try:
            stop_id = broker.sell_stop(sig.symbol, qty, sig.stop)["id"]
        except RuntimeError as e:
            stop_id = None  # protect() below retries once, then closes the position
            log(f"{sig.symbol} stop order failed: {e}")
        book.open[sig.symbol] = {"qty": qty, "entry": entry, "stop": sig.stop, "stop0": sig.stop,
                                 "target": sig.target, "stop_order_id": stop_id, "strategy": name,
                                 "half_at": sig.half_at, "trail": trail, "dir": d, "opened_at": opened_at}
        book.entries += 1
        positions.append({"symbol": sig.symbol, "cost_basis": qty * entry})
        state["cash"] -= qty * entry
        journal(cfg, {"time": now.isoformat(), "symbol": sig.symbol, "event": "buy", "qty": qty,
                      "price": f"{entry:.2f}", "stop": sig.stop, "target": sig.target or "",
                      "note": f"[{name}] {sig.reason}; risk ${qty * (entry - sig.stop):.2f}"})
        log(f"BUY {qty} {sig.symbol} @ {entry:.2f} stop {sig.stop} [{name}]: {sig.reason}")
        if not stop_id:
            risk_manager.protect(broker, cfg, book, journal, log, now)

    # sip_orb: stocks in play, 5-minute ORB, 9:35-10:30.
    if book.sip_watch is None and t >= strategies.SIP_SCAN_AT:
        if t > strategies.SIP_LAST_ENTRY:
            book.sip_watch = []
        else:
            try:
                book.sip_watch = sip_scan(broker, cfg, book, now, ctx)
            except RuntimeError as e:
                log(f"stocks-in-play scan failed, retrying next minute: {str(e)[:120]}")
            missing = {c["symbol"] for c in book.sip_watch or []} - set(bars)
            if missing:
                bars.update(todays_bars(broker, cfg, now, missing))
    if book.sip_watch and t <= strategies.SIP_LAST_ENTRY:
        sip_research = {s: v for s, v in research.items() if v[0] != "skip" or strategies.SIP_BINARY.search(v[1])}
        for c in book.sip_watch:
            k = f"sip_orb:{c['symbol']}"
            if k in book.traded_today or c["symbol"] not in bars:
                continue
            sig = strategies.sip_signal(c, bars[c["symbol"]], broker.latest_price(c["symbol"], cfg.data_feed))
            if sig:
                book.traded_today.append(k)
                enter(sig, research_view=sip_research)

    # control: the old 15-min ORB on the core five, strict gap and research rules.
    for sym in cfg.core_symbols:
        k = f"control:{sym}"
        if k in book.traded_today:
            continue
        sig = strategies.control_signal(sym, bars.get(sym, []), cfg.opening_range_minutes,
                                        strategies.atr(ctx["prior"].get(sym, [])))
        if not sig:
            continue
        book.traded_today.append(k)
        ok, gap_note = gap_ok(broker, cfg, sym, bars.get(sym, []), now, ctx)
        if not ok:
            journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "skip", "price": f"{sig.entry:.2f}",
                          "note": f"[control] {sig.reason}; skipped, {gap_note} exceeds {cfg.max_gap:.2%}"})
            log(f"{sym} [control] signal skipped: {gap_note}")
            continue
        enter(sig, trail="vwap")

    # noise: SPY noise-area momentum on the :00/:30 grid, with the 11:30 fallback
    # that keeps Luke's "no day without a trade" rule.
    if grid and spy and not book.flags.get("noise_done"):
        gt = time(*map(int, key.split(":")))
        d = strategies.noise_direction(spy_bars, spy_pc, ctx["sigma"])
        in_skip = strategies.NOISE_SKIP[0] <= gt <= strategies.NOISE_SKIP[1]
        fallback = d == 0 and gt >= strategies.NOISE_FALLBACK_AT and not in_skip
        if fallback:
            d = 1 if spy["close"] >= spy_bars[0]["o"] else -1
        if d and not in_skip and gt <= strategies.NOISE_LAST:
            book.flags["noise_done"] = True
            sym = "SPY" if d > 0 else "SH"
            px = broker.latest_price(sym, cfg.data_feed)
            how = (f"fallback: no band break by {strategies.NOISE_FALLBACK_AT:%H:%M}, SPY "
                   f"{'above' if d > 0 else 'below'} its open {spy_bars[0]['o']:.2f}" if fallback else
                   f"SPY {spy['close']:.2f} {'above upper' if d > 0 else 'below lower'} band "
                   f"{(bands[0] if d > 0 else bands[1]):.2f}")
            sig = strategy.Signal(sym, px, round(px * (1 - strategies.NOISE_HARD_STOP), 2), None,
                                  f"noise area {key}: {how}", strategy="noise")
            enter(sig, trail="vwap_grid" if fallback else "band", d=d,
                  cap_frac=strategies.NOISE_FALLBACK_CAP if fallback else 1.0)

    # lasthalf: 15:30, the direction of SPY's first half hour.
    if strategies.LASTHALF_AT <= t <= time(15, 31) and not book.flags.get("lasthalf_done"):
        book.flags["lasthalf_done"] = True
        d = strategies.lasthalf_direction(spy_bars, spy_pc)
        if d:
            r = f"SPY prior close to 10:00 {'up' if d > 0 else 'down'}"
            for i, sym in enumerate(["SPY", "IWM"] if d > 0 else ["SH"]):
                px = broker.latest_price(sym, cfg.data_feed)
                sig = strategy.Signal(sym, px, round(px * (1 - strategies.LASTHALF_STOP), 2), None,
                                      f"last half hour: {r}", strategy="lasthalf")
                if i == 0:
                    enter(sig)
                else:  # one slot: IWM is tracked as a shadow trade
                    q = size(cfg.capital, strategies.RISK_FRAC["lasthalf"], px, sig.stop,
                             cfg.capital * cfg.max_position_frac, cfg.fractional)
                    shadow(cfg, now, sig, q, "lasthalf has one slot; IWM tracked as shadow")


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
        try:
            if broker.clock()["is_open"]:
                step(broker, cfg, book, now)
            elif mode == "loop":
                log("market closed")
        except requests.RequestException as e:
            # A network blip (10-30: proxy error fetching bars) must not end
            # the session; resting stops cover open positions meanwhile.
            if mode != "loop":
                raise
            book.save(cfg.state_path)
            log(f"network error, retrying next minute: {str(e)[:150]}")
            _time.sleep(60 - datetime.now().second + 2)
            continue
        book.save(cfg.state_path)
        if mode == "once" or now.time() >= cfg.flatten_at:
            if mode == "loop" and now.time() >= cfg.flatten_at:
                _time.sleep(5)  # let the flatten orders fill
                reconcile(broker, cfg, book, now)
                book.save(cfg.state_path)
                log(f"done for the day: P&L ${book.day_pnl:.2f}, week ${book.week_pnl:.2f}")
            return
        if mode == "loop" and not broker.clock()["is_open"]:
            if now.time() >= cfg.session_start.replace(hour=9, minute=30) or now.weekday() >= 5:
                return
            # Started before the bell (the scheduled run fires early so a late
            # scheduler doesn't cost the first breakouts): wait for the open.
        _time.sleep(60 - datetime.now().second + 2)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "check")
