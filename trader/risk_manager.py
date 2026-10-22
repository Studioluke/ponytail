"""Risk manager: the veto on every entry, the guard on every open position,
the kill switch, and the daily risk review.

Per the vault role (Agents - Day Traders/Descriptions.md), the trader cannot
make a trade the risk manager rejects. Exits are never blocked: anything that
reduces risk always goes through.

    python -m trader.risk_manager status          # limits used, kill switch, account flags
    python -m trader.risk_manager kill "reason"   # stop trading and flatten now
    python -m trader.risk_manager resume          # clear the kill switch
    python -m trader.risk_manager review [YYYY-MM-DD]   # daily risk review in Markdown
"""
import csv
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import Config
from .risk import Book

ET = ZoneInfo("America/New_York")
LIVE_ORDER_STATES = {"new", "accepted", "pending_new", "held", "accepted_for_bidding", "partially_filled"}

# What the paper record has to show before Luke is asked about real money.
GATE = {"min_trades": 30, "min_profit_factor": 1.2, "max_drawdown": 0.06}


@dataclass
class Decision:
    ok: bool
    reasons: list = field(default_factory=list)

    def __str__(self):
        return "approved" if self.ok else "; ".join(self.reasons)


# kill switch

def kill_reason(cfg):
    if os.environ.get("TRADER_KILL", "").strip() not in ("", "0"):
        return f"TRADER_KILL={os.environ['TRADER_KILL']}"
    if os.path.exists(cfg.kill_path):
        with open(cfg.kill_path) as f:
            return f.read().strip() or "kill switch file present"
    return None


def kill(cfg, reason):
    os.makedirs(os.path.dirname(cfg.kill_path) or ".", exist_ok=True)
    with open(cfg.kill_path, "w") as f:
        f.write(f"{datetime.now(ET):%Y-%m-%d %H:%M} ET {reason}\n")


def resume(cfg):
    if os.path.exists(cfg.kill_path):
        os.remove(cfg.kill_path)


# research input

def research_verdicts(cfg, day):
    """{symbol: (verdict, why)} from the market research brief for `day`
    (trader/journal/research/DATE.json), or {} if there is no brief."""
    path = os.path.join(cfg.research_dir, f"{day}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            d = json.load(f)
        return {w["symbol"]: (w.get("verdict", "ok"), w.get("why", "")) for w in d.get("watchlist", [])}
    except (ValueError, KeyError, TypeError):
        return {}


# pre-trade veto

def check_entry(cfg, book, sig, qty, now, account, positions, last_bar_time=None, last_price=None,
                research=None):
    """Every rule a new long entry must pass. Returns a Decision with every
    failed rule, not just the first, so the journal shows the whole picture."""
    no = []
    k = kill_reason(cfg)
    if k:
        no.append(f"kill switch: {k}")
    halted = book.halted(cfg)
    if halted:
        no.append(f"circuit breaker: {halted}")
    verdict, why = (research or {}).get(sig.symbol, ("ok", ""))
    if verdict == "skip":
        no.append(f"research says skip {sig.symbol}: {why}")
    if sig.symbol not in cfg.symbols:
        no.append(f"{sig.symbol} not on the approved list")
    if not (sig.stop < sig.entry < sig.target):
        no.append(f"bad bracket: stop {sig.stop} / entry {sig.entry} / target {sig.target}")
    t = now.time()
    if t < cfg.session_start or t > cfg.last_entry:
        no.append(f"outside entry window {cfg.session_start:%H:%M}-{cfg.last_entry:%H:%M} ET")
    held = {p["symbol"] for p in positions} | set(book.open)
    if sig.symbol in held:
        no.append(f"already holding {sig.symbol}")
    if len(held) >= cfg.max_open_positions:
        no.append(f"{len(held)} positions open, max {cfg.max_open_positions}")
    if qty <= 0:
        no.append("size rounds to 0")
    risk = qty * (sig.entry - sig.stop)
    cap = cfg.capital * cfg.risk_per_trade
    if risk > cap * 1.01:
        no.append(f"risk ${risk:.2f} over the ${cap:.2f} per-trade cap")
    used = sum(abs(float(p["cost_basis"])) for p in positions)
    notional = qty * sig.entry
    if used + notional > cfg.capital * 1.01:
        no.append(f"${used + notional:.2f} exposure over ${cfg.capital:.0f} capital")
    if notional > cfg.capital * cfg.max_position_frac * 1.01:
        no.append(f"${notional:.2f} position over {cfg.max_position_frac:.0%} of capital")
    if last_bar_time is not None and now - last_bar_time > timedelta(minutes=cfg.max_data_age_minutes):
        no.append(f"stale data: last bar {last_bar_time:%H:%M}, now {now:%H:%M}")
    if last_price is not None and sig.entry > 0 and abs(last_price / sig.entry - 1) > cfg.max_slippage:
        no.append(f"price moved: last {last_price:.2f} vs signal {sig.entry:.2f} "
                  f"(over {cfg.max_slippage:.2%})")
    if last_price is not None and last_price <= sig.stop:
        no.append(f"last {last_price:.2f} already at or below stop {sig.stop}")
    if account:
        if account.get("status") != "ACTIVE":
            no.append(f"account status {account.get('status')}")
        if account.get("trading_blocked") or account.get("account_blocked"):
            no.append("account blocked by broker")
        # FINRA pattern-day-trader rule: under $25k, a 4th day trade in 5
        # days flags the account. Paper holds $100k, live $300 would not.
        if float(account.get("equity", 0)) < 25_000 and int(account.get("daytrade_count", 0)) >= 3:
            no.append(f"PDT guard: {account['daytrade_count']} day trades in 5 days under $25k equity")
    return Decision(not no, no)


# position guard

def protect(broker, cfg, book, journal, log, now):
    """Every open trade must have a live stop order. Re-place a missing one;
    if that fails, close the position. Returns the symbols acted on."""
    acted = []
    for sym, t in list(book.open.items()):
        if t.get("exit_reason"):
            continue
        status = None
        if t.get("stop_order_id"):
            try:
                status = broker.order(t["stop_order_id"])["status"]
            except RuntimeError:
                status = "unknown"
        if status in LIVE_ORDER_STATES or status == "filled":
            continue
        acted.append(sym)
        try:
            t["stop_order_id"] = broker.sell_stop(sym, t["qty"], t["stop"])["id"]
            note = f"stop order was {status or 'missing'}; re-placed at {t['stop']}"
        except RuntimeError as e:
            try:
                broker.close_position(sym)
            except RuntimeError:
                pass  # no position to close (the buy never filled); flatten at 3:45 still sweeps
            t["exit_reason"] = "risk"
            note = f"stop order was {status or 'missing'} and could not be re-placed ({e}); closed position"
        journal(cfg, {"time": now.isoformat(), "symbol": sym, "event": "risk_guard", "qty": t["qty"],
                      "stop": t["stop"], "note": note})
        log(f"RISK {sym}: {note}")
    return acted


# review

def _rows(cfg):
    if not os.path.exists(cfg.journal_path):
        return []
    with open(cfg.journal_path) as f:
        return list(csv.DictReader(f))


def closed_trades(rows):
    """Pair each exit with the buy before it. Returns dicts with day, symbol,
    qty, entry, stop, pnl, risk ($ at entry), r, how."""
    open_, out = {}, []
    for r in rows:
        if r["event"] == "buy":
            open_[r["symbol"]] = r
        elif r["event"].startswith("exit_") and r["symbol"] in open_:
            b = open_.pop(r["symbol"])
            qty, entry, stop = float(b["qty"]), float(b["price"]), float(b["stop"])
            risk = qty * (entry - stop)
            pnl = float(r["pnl"] or 0)
            out.append({"day": r["time"][:10], "symbol": r["symbol"], "qty": qty, "entry": entry, "stop": stop,
                        "pnl": pnl, "risk": risk, "r": pnl / risk if risk > 0 else 0.0,
                        "how": r["event"][5:]})
    return out


def stats(trades, capital):
    wins = [t["pnl"] for t in trades if t["pnl"] > 0]
    losses = [-t["pnl"] for t in trades if t["pnl"] < 0]
    eq = peak = dd = 0.0
    streak = worst_streak = 0
    for t in trades:
        eq += t["pnl"]
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
        streak = streak + 1 if t["pnl"] < 0 else 0
        worst_streak = max(worst_streak, streak)
    n = len(trades)
    return {"trades": n, "pnl": eq, "win_rate": len(wins) / n if n else 0.0,
            "profit_factor": sum(wins) / sum(losses) if losses else (float("inf") if wins else 0.0),
            "avg_r": sum(t["r"] for t in trades) / n if n else 0.0,
            "max_dd": dd, "max_dd_pct": dd / capital if capital else 0.0, "losing_streak": worst_streak}


def breaches(cfg, trades, rows):
    """Things that should never happen. Any of these blocks live trading."""
    out = []
    cap = cfg.capital * cfg.risk_per_trade
    for t in trades:
        if t["risk"] > cap * 1.01:
            out.append(f"{t['day']} {t['symbol']}: entered with ${t['risk']:.2f} risk, cap ${cap:.2f}")
        if t["r"] < -1.5:
            out.append(f"{t['day']} {t['symbol']}: lost {t['r']:.2f}R, stop did not hold")
    for r in rows:
        if r["event"] == "risk_guard":
            out.append(f"{r['time'][:16]} {r['symbol']}: unprotected position ({r['note']})")
    return out


def gate(s, n_breaches):
    checks = [
        (f"At least {GATE['min_trades']} closed paper trades", s["trades"] >= GATE["min_trades"], f"{s['trades']}"),
        (f"Profit factor at least {GATE['min_profit_factor']}", s["profit_factor"] >= GATE["min_profit_factor"],
         f"{s['profit_factor']:.2f}"),
        ("Positive average R", s["avg_r"] > 0, f"{s['avg_r']:+.2f}R"),
        (f"Max drawdown under {GATE['max_drawdown']:.0%} of capital", s["max_dd_pct"] < GATE["max_drawdown"],
         f"{s['max_dd_pct']:.2%}"),
        ("No risk rule breaches", n_breaches == 0, f"{n_breaches}"),
    ]
    return checks, all(ok for _, ok, _ in checks)


def review(cfg, day, book=None, account=None):
    rows = _rows(cfg)
    all_trades = closed_trades(rows)
    today = [t for t in all_trades if t["day"] == day.isoformat()]
    todays_rows = [r for r in rows if r["time"][:10] == day.isoformat()]
    book = book or Book.load(cfg.state_path)
    k = kill_reason(cfg)
    lines = [f"## Risk review {day:%A %Y-%m-%d}", ""]
    lines.append(f"**Kill switch:** {'ON, ' + k if k else 'off'}")
    if account:
        lines.append(f"**Account:** {account.get('status')}, equity ${float(account.get('equity', 0)):,.2f}, "
                     f"day trades (5d) {account.get('daytrade_count', 'n/a')}, "
                     f"PDT flag {account.get('pattern_day_trader', 'n/a')}")
    lines += ["", "### Limits", "| Rule | Used | Limit |", "|---|---|---|"]
    if book.day == day.isoformat():
        lines += [f"| Daily loss | ${book.day_pnl:.2f} | -${cfg.max_daily_loss * cfg.capital:.2f} |",
                  f"| Losing trades today | {book.day_losses} | {cfg.max_daily_losses} |",
                  f"| Weekly loss | ${book.week_pnl:.2f} | -${cfg.max_weekly_loss * cfg.capital:.2f} |"]
    else:
        lines.append(f"| Daily/weekly loss | no state for this day | -2% / -5% |")
    lines += [f"| Risk per trade | max ${max([t['risk'] for t in today], default=0):.2f} today | "
              f"${cfg.capital * cfg.risk_per_trade:.2f} |",
              f"| Open positions | {len(book.open)} now | {cfg.max_open_positions} |", ""]

    lines += ["### Trades today"]
    if today:
        lines += ["| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |", "|---|---|---|---|---|---|---|---|"]
        lines += [f"| {t['symbol']} | {t['qty']:g} | {t['entry']:.2f} | {t['stop']:.2f} | {t['risk']:.2f} | "
                  f"{t['pnl']:.2f} | {t['r']:+.2f} | {t['how']} |" for t in today]
    else:
        lines.append("No closed trades.")
    vetoes = [r for r in todays_rows if r["event"] in ("risk_block", "risk_guard", "halted", "kill")]
    if vetoes:
        lines += ["", "**Risk actions:**"]
        lines += [f"- {r['time'][11:16]} {r['symbol'] or ''} {r['event']}: {r['note']}" for r in vetoes]
    lines.append("")

    s = stats(all_trades, cfg.capital)
    br = breaches(cfg, all_trades, rows)
    lines += ["### Since paper trading began",
              f"{s['trades']} trades, P&L ${s['pnl']:.2f}, win rate {s['win_rate']:.0%}, "
              f"profit factor {s['profit_factor']:.2f}, average {s['avg_r']:+.2f}R, "
              f"max drawdown ${s['max_dd']:.2f} ({s['max_dd_pct']:.2%}), longest losing streak {s['losing_streak']}.", ""]
    if br:
        lines += ["**Breaches:**", *[f"- {b}" for b in br], ""]
    checks, ready = gate(s, len(br))
    lines += ["### Live-money gate", "| Check | Pass | Value |", "|---|---|---|"]
    lines += [f"| {name} | {'yes' if ok else 'no'} | {val} |" for name, ok, val in checks]
    lines += ["", f"**Verdict:** {'meets the gate; Luke decides on live' if ready else 'stay on paper'}", ""]
    return "\n".join(lines)


def write_review(cfg, day, text):
    path = os.path.join(cfg.notes_dir, f"risk-review-{day.isoformat()}.md")
    os.makedirs(cfg.notes_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(text + "\n")
    return path


def main(argv):
    cfg = Config()
    cmd = argv[0] if argv else "status"
    if cmd == "kill":
        reason = " ".join(argv[1:]) or "manual kill"
        kill(cfg, reason)
        print(f"kill switch ON: {reason}")
        try:
            from .broker import Broker
            Broker().flatten()
            print("flattened all positions and cancelled open orders")
        except (KeyError, RuntimeError) as e:
            print(f"could not flatten now ({e}); the loop flattens on its next pass")
    elif cmd == "resume":
        resume(cfg)
        print("kill switch off")
    elif cmd in ("status", "review"):
        day = date.fromisoformat(argv[1]) if cmd == "review" and len(argv) > 1 else datetime.now(ET).date()
        account = None
        try:
            from .broker import Broker
            account = Broker().account()
        except (KeyError, RuntimeError):
            pass
        text = review(cfg, day, account=account)
        print(text)
        if cmd == "review":
            print(f"\nwritten to {write_review(cfg, day, text)}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
