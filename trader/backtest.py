"""Replay the live strategy and risk rules on historical 1-minute bars.

    python -m trader.backtest 2026-07-01 2026-10-20

Fills are simplified: entry at the signal bar's close, and if a bar touches
both the stop and the target we assume the stop hit first. No slippage or
fees beyond `slippage` per share each way, so treat results as optimistic.
"""
import sys
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from . import strategy
from .config import Config
from .risk import Book, size

ET = ZoneInfo("America/New_York")


def _et(b):
    return datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)


def split_days(bars):
    days = defaultdict(list)
    for b in bars:
        t = _et(b)
        if (9, 30) <= (t.hour, t.minute) < (16, 0):
            days[t.date()].append(b)
    return days


def simulate(bars_by_symbol, cfg, slippage=0.01):
    book, trades = Book(), []
    held = []  # (entry_time, exit_time, cost) of today's trades, to cap capital in use
    per_day = {s: split_days(bs) for s, bs in bars_by_symbol.items()}
    all_days = sorted({d for days in per_day.values() for d in days})
    for day in all_days:
        iso = day.isocalendar()
        book.roll(day.isoformat(), f"{iso.year}-W{iso.week:02d}")
        held = []
        for sym in cfg.symbols:
            bars = per_day.get(sym, {}).get(day, [])
            if book.halted(cfg):
                break
            for i in range(cfg.opening_range_minutes + 1, len(bars) + 1):
                t = _et(bars[i - 1]).time()
                # A bar stamped 09:40 closes at 09:41, which is when we'd act.
                if t < cfg.session_start or t > cfg.last_entry:
                    continue
                sig = strategy.check(sym, bars[:i], cfg.opening_range_minutes, cfg.reward_risk)
                if not sig:
                    continue
                entry = sig.entry + slippage
                now = _et(bars[i - 1])
                in_use = sum(c for a, b, c in held if a <= now < b)
                qty = size(cfg.capital, cfg.risk_per_trade, entry, sig.stop, cfg.capital - in_use)
                if qty < 1:
                    break
                exit_px, how, exit_t = None, "close", _et(bars[-1])
                for b in bars[i:]:
                    exit_t = _et(b)
                    if _et(b).time() >= cfg.flatten_at:
                        exit_px = b["o"]
                        break
                    if b["l"] <= sig.stop:
                        exit_px, how = min(sig.stop, b["o"]), "stop"
                        break
                    if b["h"] >= sig.target:
                        exit_px, how = max(sig.target, b["o"]), "target"
                        break
                if exit_px is None:
                    exit_px = bars[-1]["c"]
                exit_px -= slippage
                held.append((now, exit_t, entry * qty))
                pnl = (exit_px - entry) * qty
                book.record(pnl)
                trades.append({"day": day.isoformat(), "symbol": sym, "qty": qty, "entry": round(entry, 2),
                               "exit": round(exit_px, 2), "how": how, "pnl": round(pnl, 2)})
                break
    return trades


def summary(trades, capital):
    n = len(trades)
    if not n:
        return "no trades"
    wins = [t for t in trades if t["pnl"] > 0]
    total = sum(t["pnl"] for t in trades)
    eq, peak, dd = 0.0, 0.0, 0.0
    for t in trades:
        eq += t["pnl"]
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    gross_win = sum(t["pnl"] for t in wins)
    gross_loss = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    pf = gross_win / gross_loss if gross_loss else float("inf")
    return (f"{n} trades, {len(wins)/n:.0%} winners, P&L ${total:.2f} ({total/capital:+.1%} of ${capital:,.0f}), "
            f"profit factor {pf:.2f}, max drawdown ${dd:.2f}")


def main(start, end):
    from .broker import Broker
    cfg = Config()
    bars = Broker().bars(list(cfg.symbols), "1Min", start, end, feed=cfg.data_feed)
    trades = simulate(bars, cfg)
    for t in trades:
        print(t)
    print(summary(trades, cfg.capital))


if __name__ == "__main__":
    main(*sys.argv[1:3])
