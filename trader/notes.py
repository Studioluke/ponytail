"""Write the day's journal note in Markdown: market context, every trade or
skipped signal with its reason, and running totals.

    python -m trader.notes [YYYY-MM-DD]
"""
import csv
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import strategy
from .broker import Broker
from .config import Config
from .risk import Book


def market_lines(broker, cfg, day):
    start = (day - timedelta(days=7)).isoformat()
    daily = broker.bars(list(cfg.symbols), "1Day", start, end=day.isoformat(), feed=cfg.data_feed)
    et = ZoneInfo("America/New_York")
    open_ = datetime(day.year, day.month, day.day, 9, 30, tzinfo=et)
    close = datetime(day.year, day.month, day.day, 16, 0, tzinfo=et)
    mins = broker.bars(list(cfg.symbols), "1Min", open_.isoformat(), close.isoformat(), feed=cfg.data_feed)
    rows = ["| Symbol | Prior close | Open | Gap | 15-min range | Low | High | Close | Day change | VWAP |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for sym in cfg.symbols:
        d = daily.get(sym, [])
        prior = [b for b in d if b["t"][:10] < day.isoformat()]
        bars = mins.get(sym, [])
        if not bars or not prior:
            rows.append(f"| {sym} | no data | | | | | | | | |")
            continue
        pc = prior[-1]["c"]
        o, c = bars[0]["o"], bars[-1]["c"]
        rng = strategy.opening_range(bars, cfg.opening_range_minutes)
        rows.append(f"| {sym} | {pc:.2f} | {o:.2f} | {o / pc - 1:+.2%} | "
                    f"{rng[1]:.2f}-{rng[0]:.2f} | {min(b['l'] for b in bars):.2f} | "
                    f"{max(b['h'] for b in bars):.2f} | {c:.2f} | {c / pc - 1:+.2%} | {strategy.vwap(bars):.2f} |")
    return rows


def trade_lines(cfg, day):
    if not os.path.exists(cfg.journal_path):
        return ["No trades or signals logged."]
    with open(cfg.journal_path) as f:
        rows = [r for r in csv.DictReader(f) if r["time"][:10] == day.isoformat()]
    if not rows:
        return ["No signals today: neither symbol broke above its opening range with price above VWAP "
                "inside the entry window, so the bot stayed flat."]
    out = ["| Time (ET) | Symbol | Event | Qty | Price | Stop | Target | P&L | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        t = datetime.fromisoformat(r["time"]).strftime("%H:%M")
        out.append(f"| {t} | {r['symbol']} | {r['event']} | {r['qty']} | {r['price']} | {r['stop']} | "
                   f"{r['target']} | {r['pnl']} | {r['note']} |")
    return out


def build(day):
    cfg = Config()
    broker = Broker()
    book = Book.load(cfg.state_path)
    lines = [f"## {day:%A %Y-%m-%d}", "",
             "### Market", *market_lines(broker, cfg, day), "",
             "### Trades and signals", *trade_lines(cfg, day), ""]
    if book.day == day.isoformat():
        halted = book.halted(cfg)
        lines += [f"**Day P&L:** ${book.day_pnl:.2f} ({book.day_pnl / cfg.capital:+.2%} of ${cfg.capital:.0f}) · "
                  f"**Week to date:** ${book.week_pnl:.2f} · losing trades today: {book.day_losses}"
                  + (f" · halted: {halted}" if halted else ""), ""]
    return "\n".join(lines)


if __name__ == "__main__":
    print(build(date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()))
