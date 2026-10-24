"""Exploding-stock alerts for Luke's own (manual, real-money) trading.

Scans the market during the session for stocks that suddenly rip: a big %
gain on the day on far more volume than usual, or a sharp burst in the last
15 minutes. Each hit lists the move, relative volume, the catalyst from the
news, and a risk note, because these spikes often fade.

    python -m trader.spikes            # scan now; prints alerts, records them
    python -m trader.spikes --dry-run  # scan without recording (no dedupe update)

Candidates come from Alpaca's top gainers and most-active lists (consolidated
tape). Relative volume compares today's IEX volume with the IEX 20-day
average, scaled by how much of the session has passed; IEX is a slice of the
whole tape, so the ratio is what matters, not the raw number.

Each ticker alerts once per day. Alerts are recorded in
<state dir>/<date>.json (default /mnt/project-files/day-trader/spikes when
that folder exists, else trader/journal/spikes).

Information only, never an order, and never touches the paper trader.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .broker import Broker
from .config import DATA_URL, PAPER_URL

ET = ZoneInfo("America/New_York")
SHARED_DIR = "/mnt/project-files/day-trader/spikes"
REPO_DIR = "trader/journal/spikes"

MIN_PRICE = 2.0          # below this it is a penny stock: skip
MIN_DAY_GAIN = 10.0      # % vs prior close for a day-move alert
MIN_RVOL = 3.0           # today's volume vs normal for this time of day
BURST_GAIN = 5.0         # % in the last 15 minutes for a burst alert
BURST_DAY_GAIN = 5.0     # a burst also needs at least this much on the day
BURST_RVOL = 2.0
MIN_IEX_DOLLARS = 250_000  # today's IEX dollar volume (roughly $5M+ on the whole tape)
EXCHANGES = {"NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"}
HALT = re.compile(r"\b(halt(ed)?|circuit breaker|luld|trading pause)\b", re.I)
RISKY = re.compile(r"\b(offering|direct offering|registered direct|warrants?|reverse split|dilution|atm program|"
                   r"private placement|priced? (at|an?) .*offering)\b", re.I)


def session_fraction(now):
    """Share of the 9:30-16:00 session elapsed, floored at 30 minutes' worth.

    Volume is front-loaded, so the floor keeps the first scans from calling
    every stock a volume surge."""
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    mins = (now - open_).total_seconds() / 60
    return min(max(mins, 30), 390) / 390


def state_dir():
    return SHARED_DIR if os.path.isdir(os.path.dirname(SHARED_DIR)) else REPO_DIR


def load_alerted(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"alerts": []}


def evaluate(sym, pct, snap, hist, minutes, frac):
    """Return an alert dict for one candidate, or None.

    pct: % change vs prior close (consolidated tape); snap: IEX snapshot;
    hist: prior daily IEX bars; minutes: today's IEX 1-min bars."""
    day = snap.get("dailyBar") or {}
    trade = snap.get("latestTrade") or {}
    price = trade.get("p") or day.get("c")
    if not price or price < MIN_PRICE:
        return None
    vols = [b["v"] for b in hist[-20:]]
    avg = sum(vols) / len(vols) if vols else 0
    vol = day.get("v", 0)
    rvol = vol / (avg * frac) if avg else float("inf")
    if vol * price < MIN_IEX_DOLLARS:
        return None
    burst = None
    if minutes:
        last_t = datetime.fromisoformat(minutes[-1]["t"].replace("Z", "+00:00"))
        before = [b for b in minutes if datetime.fromisoformat(b["t"].replace("Z", "+00:00")) <= last_t - timedelta(minutes=15)]
        if before:
            burst = (minutes[-1]["c"] / before[-1]["c"] - 1) * 100
    kinds = []
    if pct >= MIN_DAY_GAIN and rvol >= MIN_RVOL:
        kinds.append("day move")
    if burst is not None and burst >= BURST_GAIN and pct >= BURST_DAY_GAIN and rvol >= BURST_RVOL:
        kinds.append("15-min burst")
    if not kinds:
        return None
    prev_close = price / (1 + pct / 100)
    return {"symbol": sym, "kind": kinds, "price": round(price, 2), "pct": round(pct, 1),
            "rvol": round(rvol, 1) if rvol != float("inf") else None, "burst_15m": None if burst is None else round(burst, 1),
            "open": day.get("o"), "high": day.get("h"), "vwap": day.get("vw"), "prev_close": round(prev_close, 2),
            "gap": round((day["o"] / prev_close - 1) * 100, 1) if day.get("o") else None,
            "trade_time": trade.get("t", "")}


def risk_note(a, news, now):
    notes = []
    if a["high"] and a["price"] < a["high"] * 0.9:
        notes.append(f"already {100 - a['price'] / a['high'] * 100:.0f}% off the high (${a['high']:.2f}), fading")
    if a["vwap"] and a["price"] < a["vwap"]:
        notes.append("trading below VWAP, sellers in control")
    if a["pct"] >= 50:
        notes.append("up 50%+: parabolic moves like this usually give back a big chunk")
    if a["price"] < 10:
        notes.append("low-priced stock: wide spreads, use limit orders")
    if any(RISKY.search(n["headline"]) for n in news):
        notes.append("offering/dilution headline: shares can drop fast")
    if any(HALT.search(n["headline"]) for n in news) or _stale(a["trade_time"], now):
        notes.append("halted or volatility halts today: price can gap either way on resume")
    if not news:
        notes.append("no news found: moves without a catalyst fade more often")
    notes.append("if you buy, set a stop (e.g. under VWAP or the breakout level) and size small")
    return notes


def _stale(t, now):
    if not t:
        return False
    when = datetime.fromisoformat(re.sub(r"\.\d+", "", t).replace("Z", "+00:00"))
    return 9.75 <= now.hour + now.minute / 60 < 16 and now - when > timedelta(minutes=5)


def scan(broker=None, now=None):
    broker = broker or Broker()
    now = now or datetime.now(ET)
    frac = session_fraction(now)
    movers = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/movers", params={"top": 50})
    actives = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/most-actives",
                          params={"by": "volume", "top": 100}).get("most_actives", [])
    pct = {m["symbol"]: m["percent_change"] for m in movers.get("gainers", []) if m["price"] >= MIN_PRICE}
    assets = {a["symbol"]: a for a in broker._req("GET", f"{PAPER_URL}/v2/assets",
                                                  params={"status": "active", "asset_class": "us_equity"})}
    cands = [s for s in dict.fromkeys(list(pct) + [m["symbol"] for m in actives])
             if assets.get(s, {}).get("tradable") and assets[s]["exchange"] in EXCHANGES]
    if not cands:
        return []
    snaps = broker._req("GET", f"{DATA_URL}/v2/stocks/snapshots", params={"symbols": ",".join(cands), "feed": "iex"})
    for s in cands:  # most-actives carry no % change: work it out from the snapshot
        sn = snaps.get(s) or {}
        prev = (sn.get("prevDailyBar") or {}).get("c")
        last = (sn.get("latestTrade") or {}).get("p")
        if s not in pct and prev and last:
            pct[s] = (last / prev - 1) * 100
    cands = [s for s in cands if pct.get(s, 0) >= BURST_DAY_GAIN and s in snaps]
    if not cands:
        return []
    today = now.date().isoformat()
    hist = broker.bars(cands, "1Day", (now - timedelta(days=40)).date().isoformat(),
                       end=(now - timedelta(days=1)).date().isoformat())
    mins = broker.bars(cands, "1Min", (now - timedelta(minutes=45)).isoformat())
    out = []
    for s in cands:
        h = [b for b in hist.get(s, []) if b["t"][:10] < today]
        a = evaluate(s, pct[s], snaps[s], h, mins.get(s, []), frac)
        if not a:
            continue
        a["name"] = assets[s]["name"]
        news = broker._req("GET", f"{DATA_URL}/v1beta1/news",
                           params={"symbols": s, "start": (now - timedelta(hours=36)).isoformat(),
                                   "limit": 5, "sort": "desc"}).get("news", [])
        a["news"] = [{"time": n["created_at"], "headline": n["headline"]} for n in news]
        a["risk"] = risk_note(a, a["news"], now)
        out.append(a)
    out.sort(key=lambda a: -a["pct"])
    return out


def fmt(a):
    rv = f"{a['rvol']:.0f}x normal volume" if a["rvol"] else "volume from nothing (no recent history)"
    L = [f"**{a['symbol']}** ({a['name']}) ${a['price']:.2f}, **{a['pct']:+.1f}%** today, {rv}"
         + (f", {a['burst_15m']:+.1f}% in the last 15 min" if a["burst_15m"] and a["burst_15m"] >= BURST_GAIN else "")]
    if a["gap"] is not None and abs(a["gap"]) >= 3:
        L.append(f"Gapped {a['gap']:+.1f}% at the open; high ${a['high']:.2f}, VWAP ${a['vwap']:.2f}")
    elif a["high"]:
        L.append(f"High ${a['high']:.2f}, VWAP ${a['vwap']:.2f}")
    L.append("Catalyst: " + (a["news"][0]["headline"] if a["news"] else "none found in the news"))
    L.append("Risk: " + "; ".join(a["risk"]))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m trader.spikes")
    ap.add_argument("--dry-run", action="store_true", help="do not record alerts (no dedupe update)")
    ap.add_argument("--state-dir", default=None)
    args = ap.parse_args(argv)
    now = datetime.now(ET)
    d = args.state_dir or state_dir()
    path = os.path.join(d, f"{now.date()}.json")
    state = load_alerted(path)
    seen = {a["symbol"] for a in state["alerts"]}
    hits = [a for a in scan(now=now) if a["symbol"] not in seen]
    if not hits:
        print("NO ALERTS")
        return 0
    print(f"EXPLODING STOCKS {now:%Y-%m-%d %H:%M} ET\n")
    print("\n\n".join(fmt(a) for a in hits))
    print("\nInfo only, not advice. These are momentum spikes; many reverse the same day.")
    if not args.dry_run:
        os.makedirs(d, exist_ok=True)
        for a in hits:
            a["alerted_at"] = now.isoformat(timespec="minutes")
        state["alerts"].extend(hits)
        with open(path, "w") as f:
            json.dump(state, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
