"""Opening scan for Luke: gap-ups (earnings first) breaking their opening range.

Runs a few minutes after the open. For every stock that gapped up 5%+ it
takes the high of the first N minutes (default 5) as the opening range and
reports which ones are trading above it (breaking out) and which are still
inside it (watch for the break). Earnings gappers are listed first, since
that is where moves like GKOS +25% on 10-29 come from.

    python -m trader.gappers                       # live scan now
    python -m trader.gappers --day 2026-10-29 --at 09:40 --symbols GKOS,PRCH,CROX
                                                   # replay a past morning

Information only, never an order.
"""
import argparse
import re
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .broker import Broker
from .config import DATA_URL, PAPER_URL, Config
from .spikes import EXCHANGES, FUND, MIN_PRICE

ET = ZoneInfo("America/New_York")
MIN_GAP = 5.0                # % open vs prior close
MIN_IEX_DOLLARS = 100_000    # IEX dollar volume since the open (early in the day, so lower than spikes.py)
EARNINGS = re.compile(r"\b(earnings|results|q[1-4]|eps|revenue|guidance|beats?|raises? .*(outlook|guidance))\b",
                      re.I)


def _t(bar):
    return datetime.fromisoformat(bar["t"].replace("Z", "+00:00")).astimezone(ET)


def evaluate(sym, prev_close, minutes, open_time, orb_minutes):
    """minutes: today's 1-min bars up to now. Returns a dict or None if not a gapper."""
    if not prev_close or not minutes:
        return None
    opening = [b for b in minutes if _t(b) < open_time + timedelta(minutes=orb_minutes)]
    if not opening:
        return None
    o = opening[0]["o"]
    gap = (o / prev_close - 1) * 100
    last = minutes[-1]["c"]
    if gap < MIN_GAP or last < MIN_PRICE:
        return None
    if sum(b["v"] * b["c"] for b in minutes) < MIN_IEX_DOLLARS:
        return None
    orh = max(b["h"] for b in opening)
    return {"symbol": sym, "gap": round(gap, 1), "open": o, "orh": round(orh, 2), "last": round(last, 2),
            "pct": round((last / prev_close - 1) * 100, 1), "high": round(max(b["h"] for b in minutes), 2),
            "breaking": last > orh, "stop": round(min(b["l"] for b in opening), 2)}


def scan(broker=None, now=None, symbols=None, orb_minutes=5):
    broker = broker or Broker()
    now = now or datetime.now(ET)
    open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    assets = {a["symbol"]: a for a in broker._req("GET", f"{PAPER_URL}/v2/assets",
                                                  params={"status": "active", "asset_class": "us_equity"})}
    if symbols is None:
        movers = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/movers", params={"top": 50})
        actives = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/most-actives",
                              params={"by": "volume", "top": 100}).get("most_actives", [])
        symbols = [m["symbol"] for m in movers.get("gainers", []) if m["price"] >= MIN_PRICE]
        symbols += [m["symbol"] for m in actives] + list(getattr(Config(), "watchlist", []))
    cands = [s for s in dict.fromkeys(symbols)
             if assets.get(s, {}).get("tradable") and assets[s]["exchange"] in EXCHANGES
             and not FUND.search(assets[s]["name"])]
    if not cands:
        return []
    day = now.date()
    daily = broker.bars(cands, "1Day", (day - timedelta(days=10)).isoformat(), end=(day - timedelta(days=1)).isoformat())
    mins = broker.bars(cands, "1Min", open_time.isoformat(), end=now.isoformat())
    out = []
    for s in cands:
        prev = [b for b in daily.get(s, []) if b["t"][:10] < day.isoformat()]
        a = evaluate(s, prev[-1]["c"] if prev else None, mins.get(s, []), open_time, orb_minutes)
        if not a:
            continue
        news = broker._req("GET", f"{DATA_URL}/v1beta1/news",
                           params={"symbols": s, "start": (open_time - timedelta(hours=20)).isoformat(),
                                   "end": now.isoformat(), "limit": 5, "sort": "desc"}).get("news", [])
        a["name"] = assets[s]["name"]
        a["news"] = [n["headline"] for n in news]
        a["earnings"] = any(EARNINGS.search(h) for h in a["news"])
        out.append(a)
    out.sort(key=lambda a: (not a["earnings"], -a["gap"]))
    return out


def fmt(a):
    tag = "EARNINGS " if a["earnings"] else ""
    line = (f"**{a['symbol']}** ({a['name']}) {tag}gap {a['gap']:+.1f}%, now ${a['last']:.2f} ({a['pct']:+.1f}%), "
            f"opening-range high ${a['orh']:.2f}, range low ${a['stop']:.2f}")
    return line + "\n  Catalyst: " + (a["news"][0] if a["news"] else "none found")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m trader.gappers")
    ap.add_argument("--day", help="replay date YYYY-MM-DD (needs --symbols)")
    ap.add_argument("--at", default=None, help="replay time HH:MM ET")
    ap.add_argument("--symbols", default=None, help="comma-separated symbols instead of the live screener")
    ap.add_argument("--orb", type=int, default=5, help="opening-range minutes (default 5)")
    args = ap.parse_args(argv)
    now = datetime.now(ET)
    if args.day:
        d = date.fromisoformat(args.day)
        hh, mm = (args.at or "09:40").split(":")
        now = datetime(d.year, d.month, d.day, int(hh), int(mm), tzinfo=ET)
    syms = args.symbols.split(",") if args.symbols else None
    hits = scan(now=now, symbols=syms, orb_minutes=args.orb)
    if not hits:
        print("NO GAPPERS")
        return 0
    brk = [a for a in hits if a["breaking"]]
    watch = [a for a in hits if not a["breaking"]][:8]
    print(f"OPENING GAPPERS {now:%Y-%m-%d %H:%M} ET (opening range = first {args.orb} min)\n")
    print("BREAKING OUT (above the opening-range high):")
    print("\n".join(fmt(a) for a in brk) or "none")
    print("\nWATCH (gapped up, not above the range high yet):")
    print("\n".join(fmt(a) for a in watch) or "none")
    print("\nInfo only, not advice. A break that falls back under the range high is a failed breakout; "
          "the range low is a natural stop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
